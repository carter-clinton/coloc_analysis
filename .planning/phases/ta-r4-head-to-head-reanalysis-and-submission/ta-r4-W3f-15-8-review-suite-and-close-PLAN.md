---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8f
slug: W3f-15-8-review-suite-and-close
type: execute
wave: 15.8f
depends_on: ["ta-r4-W3f-multikey-fatal-and-chronology"]
gap_closure: true
files_modified:
  - .planning/DECISIONS.md                                                                                     # Q-158AEI DEC (AEI + AEIM quotes)
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158AEIM-reply-2026-11-26.txt  # new, committed as received
  - config/ta_r4/data_sources.yaml                                                                              # one appended entry, grch38_fasta_mapdamage (carve-out)
  - src/python/ta_r4/orientation_eaf.py                                                                         # new diagnostic-only module (carve-out)
  - tests/ta_r4/test_asthma_eur_eaf_disclosure.py                                                               # tests A and B (15.8g appends test C)
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/grch37_reference_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/grch38_reference_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_flipped.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_unflipped_control.tsv   # seeded stratified control sample
  - .planning/HANDOFF.json
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-review-suite-and-close-SUMMARY.md
autonomous: false
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Gates Q-157J and all five 2026-11-25 replies (gate_158.sh Q-158DIG Q-158R6S Q-158E7R Q-F3NL Q-158R7) pass, and Q-158R2 (gate_158r2.sh), Q-158OR, Q-158PAL and Q-158EL (gate_158a2.sh) re-gate with their pinned sha256, and every STOP reply named in a 15.8a–e SUMMARY (15.8a2–a4 included: Q-158FP/Q-158EL2, and Q-158R3/R5/R6, if any) re-gates with its pinned sha256; the 2026-11-26 replies Q-158R6G, Q-158KW, Q-158DFX, Q-158AEI and Q-158AEIM pass gate_158.sh by full file name (Q-158DFX, Q-158AEI and Q-158AEIM added here), and the tracked ones (R6G both files 4e47c20d, KW cd96833e, DFX b1b5aa00, AEI 4e47c20d) also pass `git ls-files --error-unmatch`, `git diff --quiet HEAD --`, added-in-commit == the pinned commit and sha256 == the pinned value"
    - "Q-158AEI (`Disclose, no filter (Recommended)`, fa00fcb4…96ea) and its correction Q-158AEIM (`Measure it first`, b2a13e9c…90e8, last line asserted) are recorded in one DEC entry, DEC-2026-11-26-ta-r4-asthma-eur-eaf-disclose-no-filter, both quoted with `cat` and each quote `cmp`-equal to its reply file; the DEC states that the Q-158AEI question's lift explanation was a planner's guess (ta-r4-W3f-sumstats-orientation-harmonize-PLAN.md:154-155), not a measurement"
    - "src/python/ta_r4/orientation_eaf.py (diagnostic only) rebuilds manifests/sumstats_r4_orientation_eaf.tsv byte for byte (sha256 7ad5ce50…80c0); a difference is STOP before anything is built on it. It has no side effect at import, imports nothing from tests, contains no /rs1, /share or /gpfs_common literal, and is referenced by nothing else in src, workflow, Snakefile* or config (the F4 grep pipeline is empty); `git diff --name-status $(cat $Q8/start_15_8f.txt) HEAD -- src` == `A\tsrc/python/ta_r4/orientation_eaf.py`"
    - "Both halves of the reference check are measured against pinned references reached by repo-relative paths: GRCh38 = data/r4/inputs/grch38_fasta/GRCh38_mapDamage.fa (assembly verified by its 24 primary contig lengths equal to the published GRCh38 values; registered as grch38_fasta_mapdamage in data_sources.yaml), GRCh37 = data/r4/inputs/1kg_vcf/chrN.vcf.gz (onekg_phase3_vcf); both manifests in the house format (line 1 `rel_path\tsize_bytes\tsha256\tsource`, no comment line) and test A re-checks size and sha256 of every reference file it opens"
    - "The per-row manifest has all 225 asthma EUR flipped rows with four measured tri-state columns (true / false / undetermined): grch38_ref_match (source REF vs GRCh38 at the GRCh38 position, found through lifted.bed by input line), grch37_ref_match (lifted REF vs the GRCh37 bases at the lifted span, REF bases of 1000G records inside the span only), lift_changed_ref = grch38_ref_match ∧ ¬grch37_ref_match and source_ref_not_grch38 = ¬grch38_ref_match (Kleene logic), plus catalog_ref_grch37_match = ref_match(REF_oriented, grch37_bases(CHR, POS, len(REF_oriented))) (REF_oriented's own length; indels can differ); no column name asserts a cause"
    - "An UNFLIPPED control group carries the same four columns: the asthma EUR unflipped rows of the same eaf_diffs join (same t2d EUR file, same 31 windows), sampled by a pinned rule (seed 20261127; strata class SNV/indel × |ΔEAF| > 0.2 / ≤ 0.2; every row of a > 0.2 stratum; 2,000 drawn per ≤ 0.2 stratum, all if fewer), written to manifests/sumstats_r4_orientation_eaf_asthma_eur_unflipped_control.tsv whose line 1 states the rule and each stratum's population size"
    - "The cross-tab ($Q8/aeiw_crosstab_15_8f.tsv, shown at Q-158AEIW) reports each column's true / false / undetermined counts for flipped (all 225) vs unflipped control × SNV/indel × |ΔEAF| > 0.2 / ≤ 0.2, with each control stratum's population size, so a GRCh37 mismatch that every flipped row has by construction is visible against the control and is not read as an explanation of the > 0.2 rows"
    - "The filled DRAFT (c) sentence states only measured numbers, read by the script from the manifests (it may compare flipped and control rows only through those counts); it says 'the file's REF allele' rather than 'the GRCh38 reference' wherever the GRCh38 half is undetermined; it is NOT inserted in 15.8f"
    - "Tests A and B green in a dedicated sbatch run (cascadelake; junit parsed), and every NC (in-place mutation of the file the test reads, restored by copy and sha256-equal after) makes its test fail"
    - "FULL under Slurm (cascadelake) reconciled per id against data/r4/tmp/w3f/q157/full_15_7j.xml over the nine 15.8a–e SUMMARYs plus this plan's 2 ids (expected 6 + 14 + 8 + 6 + 16 + 8 + 6 + 6 + 2 = 72 → 2,766, + 2 → 2,768 = 2,715 P / 53 S / 0 F; read from the SUMMARYs, not typed) and against full_15_8e.xml: identical by id except exactly this plan's 2 added ids, each passed"
    - "15.8f ends at a blocking STOP, Q-158AEIW, after its records are committed: the first option is non-approving (`Hold — do not insert`); the orchestrator writes Carter's reply file and states its sha256; the executor never writes or answers it"
    - "decision_rules.yaml locked: false; n_regions_min 7; no push, OSF, production fit or W4a-T3 lock; no DRAFT edit in 15.8f"
  artifacts:
    - path: "src/python/ta_r4/orientation_eaf.py"
      provides: "the 15.8a2 EAF join as an importable, side-effect-free module; per-row flipped detail; GRCh38 and GRCh37 reference reads; tri-state rules"
      exports: ["eaf_diffs", "render_eaf_manifest", "flipped_rows", "eaf_rows", "control_sample", "grch38_rows", "grch38_bases", "bases_from_records", "grch37_bases", "ref_match", "k_and", "k_not"]
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_flipped.tsv"
      provides: "one row per asthma EUR flipped row (225), measured tri-state columns"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_unflipped_control.tsv"
      provides: "seeded stratified sample of asthma EUR unflipped rows, same columns (control group)"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/grch37_reference_sha256.tsv"
      provides: "the 48 1000G Phase 3 VCF/.tbi files, house format"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/grch38_reference_sha256.tsv"
      provides: "the GRCh38 FASTA + .fai and work_EUR/lifted.bed, house format"
  key_links:
    - from: "tests/ta_r4/test_asthma_eur_eaf_disclosure.py"
      to: "src/python/ta_r4/orientation_eaf.py"
      via: "import (not a copy); byte rebuild of sumstats_r4_orientation_eaf.tsv"
      pattern: "from ta_r4 import orientation_eaf"
    - from: "tests/ta_r4/test_asthma_eur_eaf_disclosure.py"
      to: "config/ta_r4/data_sources.yaml"
      via: "reference paths read from the grch38_fasta_mapdamage and onekg_phase3_vcf entries, never typed"
      pattern: "grch38_fasta_mapdamage|onekg_phase3_vcf"
---

<objective>
Measure, for every asthma EUR flipped row, whether its REF matches GRCh38 and whether the GRCh37 reference at the lifted
position differs (Carter Q-158AEIM "Measure it first"), with comparison groups that can tell "the lift changed the
reference" apart from "flipped rows mismatch GRCh37 by construction"; fill the DRAFT (c) sentence from those numbers;
run FULL; commit the records; and STOP for Carter's approval of the wording (Q-158AEIW). Insertion, (m)/Pre-Paste, the
brief-blind review, the closing FULL and the W4a depends_on move to 15.8g
(ta-r4-W3f-15-8-insert-review-and-close-PLAN.md; split by the orchestrator at the AEIW STOP).
Output: the AEI/AEIM DEC; orientation_eaf.py (aggregate manifest rebuilt byte for byte); the GRCh38 symlink and
data_sources entry; the two reference manifests; the per-row manifest and the unflipped control manifest; tests A and B; the filled sentence and cross-tab;
FULL reconciled; HANDOFF / STATE / LOG / PLAN-INDEX / SUMMARY; the Q-158AEIW question. No DRAFT edit. No push.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-157J: file `W3f-carter-15-7j-open-items-reply-2026-11-24.txt`, sha256
`805afcd812902605dd9797d63c15fb201eae1fd2870db348182c1d38a640503e` (free text and question as in 15.8a <question>).
The five 2026-11-25 replies (question texts in 15.8a's <question> table), all re-gated here:
| QID | file | sha256 | label |
|---|---|---|---|
| Q-158DIG | `W3f-carter-15-8-Q-158DIG-reply-2026-11-25.txt` | `ea8fe4cdaf4bbcf802d65e68c75e66d3b095777f0e518e9ed57c088d3246ceb4` | `A: Exact round-trip everywhere r4 thresholds (Recommended)` |
| Q-158R6S | `W3f-carter-15-8-Q-158R6S-reply-2026-11-25.txt` | `7b3d1045f770bdea49123a85d58866501a46dbe62b0d9ddf5f9ac6bf36875b2d` | `Proceed, pin r_coloc only (Recommended)` |
| Q-158E7R | `W3f-carter-15-8-Q-158E7R-reply-2026-11-25.txt` | `43a4d89900c7225576a9edef1980716db999ca8c3193694305fca2c42376bd09` | `Add a matched-rounding column (Recommended)` |
| Q-F3NL | `W3f-carter-15-8-Q-F3NL-reply-2026-11-25.txt` | `9b4c0bb009e5262c38262da953e2a009b8c1859447bbb0975a24c68c9162b6a1` | `Keep legacy rule for QTL_legacy (Recommended)` |
| Q-158R7 | `W3f-carter-15-8-Q-158R7-reply-2026-11-25.txt` | `a9a6866eb9c4b518c7a98206273ddd55fe0cbd4e2e49c1b3d7264d2f69a261b8` | `Approve as written (Recommended)` |

Asked during 15.8b–15.8f, also re-gated here (gate_158.sh, by full file name via `F[]`, never a glob). Tracked ones
are also checked with `git ls-files --error-unmatch <f>`, `git diff --quiet HEAD -- <f>`, `git log --diff-filter=A
--format=%H -- <f>` starting with the commit below, and `sha256sum` == the pinned value (any miss = STOP):
| QID | file | sha256 | label | tracked |
|---|---|---|---|---|
| Q-158R6G | `W3f-carter-15-8-Q-158R6G-reply-2026-11-26.txt` | `e766bbbd642280d55e7e176b5887be2b033b9ac65d219a66e102b86a995d8a24` | `A: BLAS check only for r_coloc rules (Recommended)` | 4e47c20d |
| Q-158KW | `W3f-carter-15-8-Q-158KW-reply-2026-11-26.txt` | `1f641dccebaae2f6539a9e563330546e2f6867767093011e12f574e2f378b99a` | `Approve as written (Recommended)` | cd96833e |
| Q-158DFX | `W3f-carter-15-8-Q-158DFX-reply-2026-11-26.txt` | `dbe60868e73171d992d6bb204070cc372608a9cb7489b35c865168bbcbac154d` | `Fix the test (Recommended)` | b1b5aa00 (no DEC; 15.8d recorded it in its LOG/SUMMARY) |
| Q-158AEI | `W3f-carter-15-8-Q-158AEI-reply-2026-11-26.txt` | `fa00fcb41adf4e9e5778e67e68ba6408a815a5a369795cdb5f96d539f37396ea` | `Disclose, no filter (Recommended)` | 4e47c20d |
| Q-158AEIM | `W3f-carter-15-8-Q-158AEIM-reply-2026-11-26.txt` | `b2a13e9c8366d6296c42b50438188c34d1b5ce6e3aaebbe082628e1277c590e8` | `Measure it first` | untracked; committed in Task 1 step 2 |

The earlier presentation of Q-158R6G, `W3f-carter-15-8-Q-158R6G-reply-2026-11-25.txt` (tracked, 4e47c20d, sha256
`1cdfc554367b6dbac915b12aba3b4693ddb30c6e021883a9c29593bb544b55fa`), is quoted in
DEC-2026-11-26-ta-r4-blas-guard-r-coloc-rules-only as that earlier presentation; it gets the four tracked-file checks
above but is not passed through gate_reply.py (the 2026-11-26 file is the gated answer). The question text of each
2026-11-26 reply is line 1 after `Question <QID> (2026-11-26): `, copied by `sed`, not retyped. Q-158AEIM's last line
is asserted `Carter reply (verbatim, selected option): Measure it first` (`tail -n 1`) in addition to the gate.

STOP replies (Q-158R2/R3/R5/R6), if any were asked: re-gated with the sha256 pinned in their plans. Q-158R2 (asked; label `D: Harmonize r4 sumstats to one orientation (Recommended)`, sha256 `4183859f21ffe016b3384043a352a5363def84ab4b9820b410d865508d19bacb`) and the 15.8a2–a4 replies Q-158OR (`b4a87020eb0ec2965b6239c7c37941dc10207854852e9e7dc555b4990ae6646a`), Q-158PAL (`b5cde5c3f787a5c3bdd74c2863398898097183cf07bc85f429d9fbd8394fec13`), Q-158EL (`f4ecd06606a6f9eb828b57a304da1663078e888494853818ba124ea3618b409c`), labels as in ta-r4-W3f-sumstats-orientation-harmonize-PLAN.md and …-eligibility-and-draft-PLAN.md.

Q-158AEIW (this plan's question, asked at the Task 4 STOP). The reply file has exactly two lines:
- line 1: `Question Q-158AEIW (<YYYY-MM-DD>): DRAFT (c) asthma EUR EAF sentence, filled from the measurement you asked
  for in Q-158AEIM. Sentence: «<$Q8/aeiw_sentence_15_8f.txt, verbatim, inline>». Insert this sentence? Tables:
  data/r4/tmp/w3f/q158/aeiw_crosstab_15_8f.tsv sha256 <…>; data/r4/tmp/w3f/q158/aeiw_rows_15_8f.tsv sha256 <…>`
  (the two values from `$Q8/aeiw_tables_15_8f.sha256`);
- line 2: `Carter reply (verbatim, selected option): <label>`.
The tables are shown to Carter separately by the orchestrator: the cross-tab for BOTH groups (all <n> flipped rows and
the seeded unflipped control, with its sampling rule and stratum population sizes) by SNV/indel × |ΔEAF| > 0.2 / ≤ 0.2
for grch38_ref_match, grch37_ref_match, lift_changed_ref, source_ref_not_grch38 and catalog_ref_grch37_match, and the
rows table (the <k> flipped rows above 0.2, all columns). Options, in this order (yolo / auto-advance selects the FIRST
option at a blocking gate, so the first is non-approving): `Hold — do not insert` / `Approve as written` / `Reword (give
the wording)` / `Leave the reference comparison out of the sentence`. No option is marked Recommended. The ORCHESTRATOR
writes the reply byte-for-byte as `W3f-carter-15-8-Q-158AEIW-reply-<YYYY-MM-DD>.txt` and states its sha256 in the 15.8g
resume message; 15.8g pins that value and re-checks both table sha256 values. The executor of 15.8f never writes,
answers or edits it.
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-harmonize-SUMMARY.md
@data/r4/sumstats/liftover_strand/script_used.sh

**Standing rules:** 15.8 shared protocol; memories feedback_a_test_must_discriminate_between_hypotheses (the
comparison groups), feedback_green_assertion_needs_a_negative_control, feedback_negative_control_defeated_by_bytecode_cache
(NCs run with PYTHONDONTWRITEBYTECODE=1), feedback_gsd_automode_bypasses_blocking_fire_gates (AEIW option order).

**What is measured and what is not.** Measured (15.8a2 SUMMARY lines 173-176, from identities.py): the asthma EUR
flipped rows are 225 (204 SNVs + 21 indels); 19 of 225 have |ΔEAF| > 0.2 vs t2d EUR; 14 of those 19 are indels; the
SNV subset gives 204 / 0.0225 / 5. NOT measured: "where the GRCh38→GRCh37 lift changed the reference allele" — a
planner's guess (ta-r4-W3f-sumstats-orientation-harmonize-PLAN.md:154-155), repeated in the Q-158AEI question and
corrected by Q-158AEIM. script_used.sh changes only POS: it keeps the GRCh38 REF/ALT, complements minus-strand SNVs
and drops minus-strand non-SNVs, so "the GRCh38 input vs the lifted file" is 0 by construction and is NOT the
measurement. The source file's BUILD column says GRCh37 although the file is GRCh38 (memory project_asthma_eur_is_grch38);
grch38_ref_match measures that premise row by row instead of trusting either label.

**Hypotheses the columns must tell apart.** H-lift: at the > 0.2 rows the source REF is the GRCh38 base and the GRCh37
base at the lifted span differs (lift_changed_ref true more often above 0.2 than at or below it). H-construction: a
flipped row's REF is, by definition of "flipped", the catalog's ALT, so grch37_ref_match false may hold for nearly all
225 rows in both |ΔEAF| groups; then it explains nothing about the > 0.2 rows. H-source: the source REF is not the GRCh38
base (source_ref_not_grch38 true), i.e. the input itself is mis-specified at those rows. Splitting the flipped rows at 0.2 cannot
test H-construction (every flipped row may mismatch GRCh37 for the same reason), so an UNFLIPPED control group of the
same file, join and windows carries the same columns: if grch37_ref_match is false at a similar rate in unflipped rows,
or true in flipped rows only where the catalog's REF is the GRCh37 base, the counts show it. Only the counts by group
can separate these; the sentence reports them and draws no causal conclusion.

**References (searched 2026-11-26, planner).**
- GRCh37 FASTA: none under /rs1/researchers/c/ckclinto (every top-level directory, full depth, all finds rc 0;
  miniconda3, conda_pkgs, conda-tmp, claude-cache skipped), /share/clintonlab/ckclinto (depth 6) or the repo's data/
  (depth 6). So the GRCh37 half uses the 1000G Phase 3 VCFs via the registered repo-relative symlink
  `data/r4/inputs/1kg_vcf` (data_sources.yaml `onekg_phase3_vcf`, build GRCh37, `checksum: null`; also read by
  src/snakemake/rules/ta_r4_panels_afr_ukb.smk as ONEKG_VCF_R4). Headers: `##source=1000GenomesPhase3Pipeline`,
  `##reference=…/phase2_reference_assembly_sequence/hs37d5.fa.gz`, `##contig=<ID=22,assembly=b37,…>`; release 20130502
  per the phase-00 config; 24 chromosomes (1-22, X, Y), `.vcf.gz` + `.tbi` each; no download log on disk.
- GRCh38 FASTA: `GRCh38_mapDamage.fa` + `.fai` in /rs1/researchers/c/ckclinto/GRCh38_genome/GRCh38_mapDamage/ (455
  contigs, bare names `1`…`22`, `X`, `Y`, no `_alt`). Planner check: its 24 primary contig lengths equal the published
  GRCh38 values (chr1 248,956,422 … Y 57,227,415; 24/24). Usable for the GRCh38 half only. It gets a repo-relative
  symlink `data/r4/inputs/grch38_fasta` → that directory (data/r4 is gitignored; the link is recorded in the LOG and
  in the data_sources entry) and the entry `grch38_fasta_mapdamage` (name, url `data/r4/inputs/grch38_fasta`,
  license `GRCh38 (Genome Reference Consortium, public); provenance: local build GRCh38_mapDamage, primary contig
  lengths verified`, public: true, build: GRCh38, checksum: null with
  the per-file pins in manifests/grch38_reference_sha256.tsv).
- Why `checksum: null` stays for both entries: each is a directory of files and the yaml checksum field holds one
  file's md5/size; the per-file sha256 pins live in the two manifests (LOG states this, and that the GRCh37 pin also
  covers the VCFs ta_r4_panels_afr_ukb.smk reads).

**GRCh38 position of a row: through work_EUR/lifted.bed by input line, not by SNP_ID + alleles.** lifted.bed
(data/r4/sumstats/liftover_strand/work_EUR/lifted.bed, untracked, pinned in grch38_reference_sha256.tsv) is the lift's
own record: one line per lifted input row, name column = that row's input line number (script_used.sh writes `NR`,
header = line 1), strand in column 6. Why: it identifies the GRCh38 row the lifted row came from without depending on
SNP_ID being present or unique, and gives the strand needed to compare a minus-strand SNV correctly; a SNP_ID + allele
join would have to undo the complement and could match several input rows. Procedure: candidates = lifted.bed lines with
chrom `chr<CHR>` (23 → X) and end == lifted POS; read those input lines from
data/processed/sumstats_harmonized/asthma.EUR.tsv.bgz (pinned 22b2807551ca…da137 in sumstats_r4_sha256.tsv; re-checked)
by line number; keep the candidates whose SNP_ID equals the lifted row's and whose REF/ALT equal the lifted REF/ALT
(strand `+`) or their complements (strand `-`); exactly one must remain, else STOP.

**Column rules (tri-state; values `true` / `false` / `undetermined`; Kleene logic for ∧ and ¬).**
- `grch38_ref_match`: `samtools faidx data/r4/inputs/grch38_fasta/GRCh38_mapDamage.fa <C>:<POS38>-<POS38+L38-1>`
  (C = CHR38, 23 → X; L38 = len(REF_GRCh38)), uppercased, == REF_GRCh38 → true, ≠ → false; undetermined if the contig
  is absent, the span passes the contig end, or a base is N.
- `grch37_ref_match`: REF_L = the lifted file's REF (the GRCh38 REF on `+`, which is every indel; its complement for a
  minus-strand SNV), L = len(REF_L), span [POS, POS+L−1] on GRCh37. Records from `tabix
  data/r4/inputs/1kg_vcf/chr<C>.vcf.gz <C>:POS-(POS+L−1)` (C: 23 → X). From each record use ONLY the bases of its REF
  string that fall inside the span (record POS+i for i < len(REF)); never use END, INFO/SVLEN or a symbolic ALT; a
  symbolic/SV record whose REF lies outside the span (tabix returns it by END overlap) contributes nothing; a record
  starting past the span end contributes nothing. Records covering the same position must agree (else STOP).
  `grch37_bases` = the L bases with `.` at uncovered positions. true if all L covered and all equal REF_L; false if any
  covered base differs; undetermined otherwise.
- `lift_changed_ref` = grch38_ref_match ∧ ¬grch37_ref_match. `source_ref_not_grch38` = ¬grch38_ref_match.
- `catalog_ref_grch37_match` = ref_match(REF_oriented, grch37_bases(CHR, POS, len(REF_oriented))): the oriented
  (catalog-orientation) REF against GRCh37 at its own length, which can differ from len(REF) for an indel. It shows
  directly whether the catalog's REF is the GRCh37 base (the by-construction hypothesis).
- An `undetermined` value is never counted as true or false; a GRCh37 FASTA (hs37d5.fa.gz from the VCF header URL)
  would remove the GRCh37 undetermined rows; downloading it is Carter's call (HANDOFF item if any remain).

**Forbidden:** analysis-code edits; any fit; any DRAFT edit; removing any HANDOFF string. **Carve-out:** (1) the new
module src/python/ta_r4/orientation_eaf.py: reads the oriented sumstats, the pinned references and the lift record, and
returns data; the manifests are written by a `$Q8` driver script, not by the module; tool and reference paths are
arguments (no /rs1, /share or /gpfs_common literal: test_storage_on_rs1 scans src/python/ta_r4 and config/ta_r4); it
does not import tests.ta_r4; `git grep -l orientation_eaf -- src workflow 'Snakefile*' config | grep -vx src/python/ta_r4/orientation_eaf.py` is empty (tests
and .planning necessarily name it). (2) one appended data_sources.yaml entry (config/ta_r4 is a LOCKED_PATHS directory
hashed at the W4a-T3 lock, which has not happened; every pre-existing entry asserted equal after, by yaml load). It does
not edit or import data/r4/tmp/w3f/q158/a2/identities.py.
</context>

<interfaces>
From src/python/ta_r4/sumstats_orient.py (use, do not modify):
```python
HEADER = ["CHR", "POS", "REF", "ALT", "BETA", "SE", "P", "EAF", "N", "SNP_ID", "TRAIT", "ANCESTRY", "BUILD"]
CATALOG_SOURCES  # asthma EUR source = data/r4/sumstats/asthma.EUR.grch37_lifted_strand.tsv.bgz
def oriented_path(trait, anc) -> str
def windows(repo=".") -> list[tuple[str, str, int, int]]      # (region_safe, chr, start, end), 31 windows
def catalog_keys_by_region(wins, repo=".") -> dict
def row_class(f, cat) -> str                                   # exact / swapped_only / both / absent
def is_palindromic(ref, alt) -> bool
```
From src/python/ta_r4/collector_drop_audit.py: `def norm_key(chrom, pos, ref, alt)`.
Tools (passed in, never literal in src): tabix and samtools from /rs1/researchers/c/ckclinto/conda_envs/hlp_haplogroups/bin/
(tests/ta_r4/test_sumstats_orient.py `TABIX`; tests may hold tool paths, src may not).

The 15.8a2 EAF join to move into the module is data/r4/tmp/w3f/q158/a2/identities.py from `# EAF diagnostic (not a
filter)` to `say("wrote", out)`: REF map `{"EUR": ("t2d","EUR"), ("t2d","AFR"): ("asthma","AFR"), ("stroke","AFR"):
("asthma","AFR"), ("asthma","AFR"): ("t2d","AFR")}`; per (source, window): reference rows keyed by `norm_key(*f[:4])` →
`num(f[7])`; source and oriented rows zipped (lengths asserted equal); skip `row_class(fs, cats[rs]) == "absent"` and
`is_palindromic(fs[2], fs[3])`; skip non-numeric EAF on either side; class flipped iff `swapped_only`; header comment
line + `trait ancestry class reference_file n median_abs_delta_eaf n_above_0.2`, medians `f"{…:.4f}"`, rows in
CATALOG_SOURCES × (flipped, unflipped) order, `lineterminator="\n"`.

New module contract (orientation_eaf.py; repo-relative paths under an explicit `repo`):
```python
def eaf_diffs(repo: str, tabix: str) -> dict          # {(trait, anc, cls, ref_file): [abs_delta, ...]} as identities.py
def render_eaf_manifest(diffs: dict) -> str           # exact text of manifests/sumstats_r4_orientation_eaf.tsv
def flipped_rows(repo, tabix, trait="asthma", anc="EUR") -> list[dict]
    # the rows eaf_diffs counts for (trait, anc, "flipped"), same order: region_safe, CHR, POS, SNP_ID, REF, ALT
    # (lifted source), REF_oriented, ALT_oriented, class ("SNV" iff len(REF)==len(ALT)==1 else "indel"),
    # EAF, EAF_reference, abs_delta_eaf
def eaf_rows(repo, tabix, trait, anc, cls) -> list[dict]       # flipped_rows generalised: cls "flipped" / "unflipped"
def control_sample(rows, seed=20261127, n_per_stratum=2000) -> list[dict]
    # strata (class, abs_delta_eaf > 0.2); every row of a > 0.2 stratum; from each <= 0.2 stratum
    # random.Random(seed).sample(sorted by (CHR, POS, REF, ALT, SNP_ID), min(n, N)); output in eaf_diffs order;
    # each row carries stratum and stratum_n (population size)
def grch38_rows(rows, input_bgz: str, lifted_bed: str) -> list[dict]
    # per row: input_line, strand, CHR_GRCh38, POS_GRCh38, REF_GRCh38, ALT_GRCh38 (rule in <context>; raises on 0 or >1)
def grch38_bases(chrom, pos, length, fasta: str, samtools: str) -> str | None   # None = undetermined
def bases_from_records(pos: int, length: int, records: list[tuple[int, str]]) -> str   # (record POS, REF); '.' uncovered
def grch37_bases(chrom, pos, length, vcf_dir: str, tabix: str) -> str           # tabix + bases_from_records; 23 -> X
def ref_match(ref: str, bases: str | None) -> str      # "true" / "false" / "undetermined" per <context>
def k_and(a: str, b: str) -> str; def k_not(a: str) -> str                      # Kleene on the three values
```
</interfaces>

<new_tests>
tests/ta_r4/test_asthma_eur_eaf_disclosure.py; 15.8f owns 2 junit ids (no parametrize); 15.8g appends test C
(`test_draft_asthma_eaf_sentence_matches_the_manifests`), which cannot be green before the sentence is inserted.
Reference paths are read from config/ta_r4/data_sources.yaml (`onekg_phase3_vcf.url`, `grch38_fasta_mapdamage.url`).
- A. `test_asthma_eur_flipped_eaf_manifests_rederive` (r4_heavy): (a) `render_eaf_manifest(eaf_diffs(...))` == the bytes
  of manifests/sumstats_r4_orientation_eaf.tsv; (b) both reference manifests: line 1 == `rel_path\tsize_bytes\tsha256\tsource`,
  every reference file opened (VCF + .tbi per chromosome read, FASTA + .fai, lifted.bed) is listed with matching size and
  sha256, and the input's sha256 == its sumstats_r4_sha256.tsv pin; the FASTA's 24 primary .fai lengths == the GRCh38
  values written in the test; (c) every row of the per-row manifest and of the unflipped control manifest rebuilt (control: line 1 == the
  sampling-rule line, sample redrawn from `eaf_rows(..., "unflipped")` with the pinned seed), all columns, in order;
  control stratum population sizes sum to the aggregate asthma EUR unflipped n (216,105) and its > 0.2 strata sum to 525; (d) per-row n /
  median / n > 0.2 == the aggregate asthma EUR flipped row (225 / 0.0270 / 19); SNV / indel == 204 / 21; indels above
  0.2 == 14.
- B. `test_orientation_eaf_rules_and_import_hygiene` (quick): `bases_from_records` unit cases — an upstream multi-base
  record overlapping into the span (only its in-span bases used), a symbolic SV record whose REF is outside the span
  (ignored), a record past the span end (ignored), full and partial coverage, two records disagreeing (raises);
  `grch37_bases` maps CHR 23 to `chrX.vcf.gz` / contig X (checked on a tmp bgzipped VCF built in the test);
  `ref_match`, `k_and`, `k_not` truth tables (all 9 / 3 cases); `control_sample` on a synthetic row list is
  deterministic for the seed, keeps every > 0.2 row, and takes min(n, N) per ≤ 0.2 stratum; import hygiene — a subprocess `python -c "import
  ta_r4.orientation_eaf"` (PYTHONPATH=src/python, PYTHONDONTWRITEBYTECODE=1) from an empty tmp cwd leaves the tmp dir
  empty and the three manifests' sha256 and mtime_ns unchanged; `ast` of the module has no import of `tests` and no
  /rs1, /share or /gpfs_common literal.
Expected FULL for 15.8f: full_15_8e.xml (expected 2,766) + 2 = 2,768 = 2,715 P / 53 S / 0 F. 15.8g: 2,768 + 1 = 2,769.
</new_tests>

<tasks>

<task type="auto">
  <name>Task 1: gates; AEI + AEIM DEC; references verified, linked, registered and pinned (no code)</name>
  <files>.planning/DECISIONS.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158AEIM-reply-2026-11-26.txt, config/ta_r4/data_sources.yaml, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/grch37_reference_sha256.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/grch38_reference_sha256.tsv</files>
  <read_first>
    - the nine 15.8a–e SUMMARYs (15.8a, 15.8a2, 15.8a3, 15.8a4, 15.8b, 15.8c, 15.8c2, 15.8d, 15.8e: commits, id lists, Carter replies)
    - DECISIONS.md entries DEC-2026-11-26-ta-r4-blas-guard-r-coloc-rules-only and DEC-2026-11-26-ta-r4-draft-k-blas-wording (two-quote DEC format)
    - tests/ta_r4/test_storage_on_rs1.py (manifest_violations, data_source_violations, r4_scan_paths)
  </read_first>
  <action>
    1. `git rev-parse HEAD > $Q8/start_15_8f.txt`; `bash $Q8/gate_157j.sh`; add Q-158DFX, Q-158AEI and Q-158AEIM to
       gate_158.sh as the Q-158KW block is written (sha256, label, `sed`-copied question, `F[]` full file name, GATE_NC_*
       hooks); `bash $Q8/gate_158.sh Q-158DIG Q-158R6S Q-158E7R Q-F3NL Q-158R7 Q-158R6G Q-158KW Q-158DFX Q-158AEI
       Q-158AEIM`; three NCs per new entry as 15.8b's (GATE_NC_MUTATE=1, GATE_NC_LABEL, one GATE_NC_SHA character → exit 2
       each; real gate rc 0 after) → `$Q8/gate_nc_15_8f.txt`; the AEIM `tail -n 1` assert; the four tracked-file checks of
       <question> on R6G (both files), KW, DFX and AEI; `bash $Q8/gate_158r2.sh`; `bash $Q8/gate_158a2.sh Q-158OR Q-158PAL
       Q-158EL`; re-gate any STOP reply with its pinned sha256. All in `$Q8/gate_15_8f.txt`. Any failure = STOP, nothing edited.
    2. DECISIONS.md (one script; copy to `$Q8/DECISIONS.pre_15_8f.md` first): `DEC-2026-11-26-ta-r4-asthma-eur-eaf-disclose-no-filter`
       (Decider Carter 2026-11-26; flip rule stays by allele key, no frequency filter (Q-158PAL A); the diagnostic is
       disclosed in DRAFT (c) after measurement, wording by Q-158AEIW; the Q-158AEI question's "lift changed the reference
       allele" was a planner's guess (harmonize PLAN:154-155), corrected by Q-158AEIM; reply paths and sha256 of both;
       Not authorized as the 15.8 entries). Both replies appended with `cat` between ```text fences, AEI first; each quote
       extracted back and `cmp`-equal to its reply file; the rest of DECISIONS.md byte-equal to the pre copy (else STOP).
       Commit `docs(ta-r4-W3f): Carter Q-158AEI + Q-158AEIM (measure first) reply + DEC (15.8f)`, explicit paths:
       DECISIONS.md and the AEIM reply only.
    3. GRCh38 reference: under sbatch, assert the .fai's 24 primary contig lengths equal the published GRCh38 values
       (1 248956422, 2 242193529, 3 198295559, 4 190214555, 5 181538259, 6 170805979, 7 159345973, 8 145138636,
       9 138394717, 10 133797422, 11 135086622, 12 133275309, 13 114364328, 14 107043718, 15 101991189, 16 90338345,
       17 83257441, 18 80373285, 19 58617616, 20 64444167, 21 46709983, 22 50818468, X 156040895, Y 57227415; else STOP);
       `ln -s` the directory to `data/r4/inputs/grch38_fasta` (refuse if it exists and points elsewhere); append the
       `grch38_fasta_mapdamage` entry of <context> to data_sources.yaml (one script; every prior entry equal after by yaml
       load; test_storage_on_rs1.py, test_data_sources_labels.py, test_sumstats_orient_consumers.py and
       test_sumstats_build.py green).
    4. Pins (sbatch): manifests/grch37_reference_sha256.tsv = all 48 files under data/r4/inputs/1kg_vcf (`chrN.vcf.gz`,
       `chrN.vcf.gz.tbi`, N = 1-22, X, Y), rel_path as `data/r4/inputs/1kg_vcf/…`, source
       `##source=1000GenomesPhase3Pipeline; reference hs37d5 (release 20130502)`; manifests/grch38_reference_sha256.tsv =
       `data/r4/inputs/grch38_fasta/GRCh38_mapDamage.fa` and `.fai` (source `GRCh38 by 24/24 primary contig lengths;
       GRCh38_mapDamage build`) and `data/r4/sumstats/liftover_strand/work_EUR/lifted.bed` (source `script_used.sh
       liftOver output; name = input line`). House format: line 1 `rel_path\tsize_bytes\tsha256\tsource`, no comment
       line. test_storage_on_rs1.py::test_manifests_parse green. LOG: why both `checksum:` stay null (<context>), and that
       the GRCh37 pin also covers the VCFs ta_r4_panels_afr_ukb.smk reads. Before pinning, `ls` once more for a GRCh37
       FASTA in the searched paths; if one exists, STOP and report.
    5. Commit `chore(ta-r4-W3f): GRCh38 FASTA registered; 1000G Phase 3 VCFs and GRCh38 FASTA pinned (15.8f)`, explicit
       paths: data_sources.yaml and the two manifests.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash data/r4/tmp/w3f/q158/gate_157j.sh && bash data/r4/tmp/w3f/q158/gate_158.sh Q-158R6G Q-158KW Q-158DFX Q-158AEI Q-158AEIM && git ls-files --error-unmatch .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158AEIM-reply-2026-11-26.txt && test "$(readlink -f data/r4/inputs/grch38_fasta)" = /rs1/researchers/c/ckclinto/GRCh38_genome/GRCh38_mapDamage && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_storage_on_rs1.py tests/ta_r4/test_data_sources_labels.py -q -p no:cacheprovider && test "$(head -1 .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/grch37_reference_sha256.tsv)" = "$(printf 'rel_path\tsize_bytes\tsha256\tsource')" && test "$(tail -n +2 .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/grch37_reference_sha256.tsv | wc -l)" = 48</automated>
  </verify>
  <done>All gates and tracked-file checks pass; the AEI + AEIM DEC is committed with cmp-equal quotes; the GRCh38 FASTA is verified by contig lengths, linked repo-relative and registered; both reference manifests are pinned in the house format; no src or test file changed.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: orientation_eaf.py (byte identity first); per-row manifest with four measured tri-state columns; tests A and B with NCs; filled sentence + cross-tab (no DRAFT edit)</name>
  <files>src/python/ta_r4/orientation_eaf.py, tests/ta_r4/test_asthma_eur_eaf_disclosure.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_flipped.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_unflipped_control.tsv</files>
  <read_first>
    - data/r4/tmp/w3f/q158/a2/identities.py (EAF block only) and data/r4/sumstats/liftover_strand/script_used.sh
  </read_first>
  <behavior>
    - A and B RED before the module exists (ImportError) and before the per-row manifest exists; GREEN after
    - render_eaf_manifest(eaf_diffs()) sha256 == 7ad5ce50abfb6255da90c7eec98d760308a96c2d1eac348d4b8194e6239080c0
    - bases_from_records(100, 2, [(99, "CAT")]) == "AT" (upstream record, in-span bases only); bases_from_records(100, 2, [(90, "N")]) == ".." (SV REF outside span); bases_from_records(100, 2, [(102, "G")]) == ".."; bases_from_records(100, 2, [(100, "A")]) == "A."
    - ref_match("AT", "AT") == "true"; ("AT", "AG") == "false"; ("AT", "A.") == "undetermined"; ("AT", "G.") == "false"; ("A", None) == "undetermined"
    - k_and("true","false") == "false"; k_and("true","undetermined") == "undetermined"; k_and("false","undetermined") == "false"; k_not("undetermined") == "undetermined"
  </behavior>
  <action>
    1. RED: write tests A and B per <new_tests>; run under sbatch (cascadelake, junit) → `$Q8/red_15_8f.txt`.
    2. Module per <interfaces>, moving the identities.py EAF block into `eaf_diffs` / `render_eaf_manifest` unchanged in
       logic. Identity before anything else: sbatch driver `$Q8/eaf_rebuild_15_8f.py` writes
       `render_eaf_manifest(eaf_diffs(".", TABIX))` to `$Q8/eaf_rebuild_15_8f.tsv`; `cmp` with the manifest and sha256 ==
       7ad5ce50…80c0. Any byte difference = STOP (record the diff; do not adjust either side without Carter). Then the
       carve-out asserts: `git grep -l orientation_eaf -- src workflow 'Snakefile*' config | grep -vx src/python/ta_r4/orientation_eaf.py` is empty; no
       `tests` import (ast); test_storage_on_rs1.py green (literal scan covers the module).
    3. Per-row manifest (sbatch driver `$Q8/eaf_rows_15_8f.py`, cascadelake): `flipped_rows` + `grch38_rows` +
       `grch38_bases` / `grch37_bases` + `ref_match` / `k_and` / `k_not` → manifests/sumstats_r4_orientation_eaf_asthma_eur_flipped.tsv.
       Line 1 is the column header (no sha256 column; no comment line): region_safe CHR POS SNP_ID REF ALT REF_oriented
       ALT_oriented class EAF EAF_reference abs_delta_eaf above_0.2 input_line strand CHR_GRCh38 POS_GRCh38 REF_GRCh38
       ALT_GRCh38 grch38_bases grch38_ref_match grch37_bases grch37_ref_match lift_changed_ref source_ref_not_grch38
       grch37_bases_oriented catalog_ref_grch37_match;
       abs_delta_eaf `repr(float)`; rows in eaf_diffs order; the sources, join and column rules are stated in the LOG
       (the manifest carries data only). Check: 225 rows; median `:.4f` 0.0270; 19 above 0.2; SNV / indel 204 / 21; 14
       indels above 0.2 — any difference = STOP for Carter. The tri-state columns have no expected values.
       Control (same driver, same join, t2d EUR reference file and 31 windows): `control_sample(eaf_rows(..., "asthma",
       "EUR", "unflipped"))` + the same five columns → manifests/sumstats_r4_orientation_eaf_asthma_eur_unflipped_control.tsv;
       line 1 `# control: asthma EUR unflipped rows of the sumstats_r4_orientation_eaf.tsv join; seed 20261127; strata
       class × (abs_delta_eaf > 0.2); all rows of > 0.2 strata; 2000 per <= 0.2 stratum (all if fewer); stratum_n =
       population`, line 2 the column header (the flipped columns + stratum stratum_n). Population sizes sum to 216,105
       and the > 0.2 strata to 525 (aggregate manifest), else STOP. The GRCh38 lookup uses one lifted.bed pass for both
       groups.
    4. Cross-tab `$Q8/aeiw_crosstab_15_8f.tsv`: for each of grch38_ref_match, grch37_ref_match, lift_changed_ref,
       source_ref_not_grch38, catalog_ref_grch37_match, the true / false / undetermined counts in the eight cells group (flipped / unflipped
       control) × class (SNV / indel) × |ΔEAF| (> 0.2 / ≤ 0.2), each control cell with its stratum_n; per group each
       column's counts sum to the group's row count (225; the sample size) — asserted. `$Q8/aeiw_rows_15_8f.tsv` = the 19 rows
       above 0.2, all columns.
    5. Base-level GRCh38 check: no `.dict` with M5 values exists beside the FASTA (planner, 2026-11-27; re-check with
       `ls`), so per-contig md5 cannot be compared; the control group's grch38_ref_match true / false / undetermined
       rate is recorded in the LOG as the base-level check of the FASTA (a low true rate among unflipped rows = STOP for
       Carter, the FASTA or the input is not what it claims). If a `.dict` with M5 appears, compare every primary
       contig's M5 to the published GRCh38 md5 instead and STOP on a difference.
    5b. Tests A and B green in one dedicated sbatch run (cascadelake; stdout `$Q8/green_ab_15_8f_<jobid>.out`, junit
       `$Q8/green_ab_15_8f_<jobid>.xml`, the only match of `green_ab_15_8f_*.xml`; job id in the LOG). NCs
       (`$Q8/nc_15_8f.txt`; each an in-place mutation of the file the test reads, sha256 before, restored by copy from
       `$Q8/nc_bak/`, sha256 equal after; PYTHONDONTWRITEBYTECODE=1): run the cheap pin NC (vi) first, then the rest; every NC sbatch job with `-t` ≥ 2× the measured green-run
       time of test A (recorded) and `--mem=64G`: (i) one abs_delta_eaf → A fails; (ii) one median in
       sumstats_r4_orientation_eaf.tsv → A fails; (iii) one value each of grch38_ref_match, grch37_ref_match,
       lift_changed_ref, source_ref_not_grch38, catalog_ref_grch37_match (true↔false, or undetermined→true) → A fails,
       five runs; (viii) one control
       row perturbed (its grch37_ref_match flipped) in the control manifest → A fails; and the control line-1 seed
       changed → A fails; (vi) one sha256
       character in grch37_reference_sha256.tsv → A fails on the pin check, and the same in grch38_reference_sha256.tsv;
       (vii) a line `open("nc_side_effect", "w").close()` appended to the module → B fails (tmp cwd not empty); the restore
       step restores the module by sha256, deletes any `nc_side_effect` it created (repo root and tmp cwd) and asserts
       `test ! -e nc_side_effect`. A test
       that does not fail on its NC = STOP.
    6. Filled sentence (script, numbers read from the manifests, never typed) → `$Q8/aeiw_sentence_15_8f.txt` (one line)
       and its sha256 → `$Q8/aeiw_sentence_15_8f.sha256`; the two tables' sha256 → `$Q8/aeiw_tables_15_8f.sha256`
       (crosstab, then rows). Counts, flipped group: n; k (> 0.2); j (indels > 0.2); m_f / m_u (`:.4f` medians rounded
       to 3 decimals); a / a_f / a_u38 = grch38_ref_match true / false / undetermined over n; a_hi / a_lo =
       grch38_ref_match true above / at or below 0.2 (the matching-row denominators); c_hi / c_lo = lift_changed_ref true
       above / at or below 0.2; g_u37 = grch37_ref_match undetermined among the a GRCh38-matching rows. Control group:
       the same with prefix u_ (u_n, u_k, u_a, u_a_f, u_a_u38, u_a_hi, u_a_lo, u_c_hi, u_c_lo, u_g_u37). Undetermined
       is always split into GRCh38-undetermined and GRCh37-undetermined; neither is attributed to the other reference.
       If a ≥ 1:
       `As a diagnostic, not a filter: in asthma EUR the <n> rows flipped to the catalog's orientation agree less well
       in effect-allele frequency with the EUR type 2 diabetes file than its other rows (median |ΔEAF| <m_f> vs <m_u>;
       <k> of <n> above 0.2, <j> of them indels). The file's REF allele matches the GRCh38 reference at <a> of the <n>
       (<a_f> do not; <a_u38> could not be checked against GRCh38); of the <a_hi> matching rows above 0.2 the GRCh37
       reference at the lifted position differs from that REF at <c_hi>, and of the <a_lo> at or below 0.2 at <c_lo>
       (<g_u37> matching rows could not be checked against the 1000 Genomes Phase 3 GRCh37 records). In a seeded sample
       of <u_n> of the file's unflipped rows (all <u_k> above 0.2 and up to 2,000 per allele class at or below it), the
       REF matches GRCh38 at <u_a> (<u_a_f> do not; <u_a_u38> could not be checked against GRCh38); of the <u_a_hi>
       matching rows above 0.2 the GRCh37 reference differs at <u_c_hi>, and of the <u_a_lo> at or below 0.2 at
       <u_c_lo> (<u_g_u37> could not be checked against the GRCh37 records). Rows are flipped by allele key and no
       frequency filter is applied.`
       If a == 0, the GRCh38 clauses become `The file's REF allele could not be confirmed against GRCh38 at any of the <n>
       (<a_f> do not match; <a_u38> could not be checked)`, and the GRCh37 clauses use x_hi / x_lo = grch37_ref_match
       false above / at or below 0.2 over all rows, with `the file's REF allele differs from the GRCh37 reference at the
       lifted position at <x_hi> of the <k> rows above 0.2 and at <x_lo> of the <n−k> at or below 0.2 (<x_u37> could not
       be checked against the 1000 Genomes Phase 3 GRCh37 records)`; the control likewise (u_x_hi, u_x_lo, u_x_u37). All
       counts printed even when 0; every denominator is printed next to its numerator; nothing causal added.
    7. Commit `feat(ta-r4-W3f): orientation_eaf diagnostic module (aggregate manifest rebuilt byte for byte); asthma EUR
       flipped rows measured against pinned GRCh38 and 1000G Phase 3 GRCh37 (15.8f)`, explicit paths: module, test file,
       per-row manifest, control manifest. Then `git diff --name-status $(cat $Q8/start_15_8f.txt) HEAD -- src` == `A\tsrc/python/ta_r4/orientation_eaf.py` (else STOP).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && test "$(sha256sum < .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf.tsv | cut -d' ' -f1)" = 7ad5ce50abfb6255da90c7eec98d760308a96c2d1eac348d4b8194e6239080c0 && test "$(git diff --name-status $(cat data/r4/tmp/w3f/q158/start_15_8f.txt) HEAD -- src)" = "$(printf 'A\tsrc/python/ta_r4/orientation_eaf.py')" && test -z "$(git grep -l orientation_eaf -- src workflow 'Snakefile*' config | grep -vx src/python/ta_r4/orientation_eaf.py)" && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import glob,xml.etree.ElementTree as E;f=glob.glob('data/r4/tmp/w3f/q158/green_ab_15_8f_*.xml');assert len(f)==1,f;N={'test_asthma_eur_flipped_eaf_manifests_rederive','test_orientation_eaf_rules_and_import_hygiene'};c=[t for t in E.parse(f[0]).iter('testcase') if t.get('name') in N];assert len(c)==2 and not [x for t in c for x in t if x.tag in ('failure','error','skipped')],c" && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_asthma_eur_eaf_disclosure.py tests/ta_r4/test_storage_on_rs1.py -q -p no:cacheprovider -k "not rederive" && test -s data/r4/tmp/w3f/q158/aeiw_sentence_15_8f.txt && test -s data/r4/tmp/w3f/q158/aeiw_crosstab_15_8f.tsv && head -1 .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_unflipped_control.tsv | grep -qF 'seed 20261127'</automated>
  </verify>
  <done>The module rebuilds the aggregate manifest byte for byte and is the only src change; the per-row manifest holds 225 rows and the control manifest a seeded stratified unflipped sample, both with four measured tri-state columns; A and B are green in their own sbatch run with every NC failing; the cross-tab, the 19-row table and the filled sentence are on disk; the DRAFT is unchanged.</done>
</task>

<task type="auto">
  <name>Task 3: FULL under Slurm, reconciled; records (HANDOFF, STATE, LOG, PLAN-INDEX, SUMMARY); commit (no push)</name>
  <files>.planning/HANDOFF.json, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-review-suite-and-close-SUMMARY.md (scratch: $Q8/full_15_8f.xml, $Q8/check_15_8f.py, $Q8/reconcile_15_8f.txt)</files>
  <action>
    1. `$Q8/close.sh 15_8f` under sbatch (protocol, `--constraint=cascadelake`, `--mem=64G` or more; 15.8e's FULL used
       the full 64G).
    2. `$Q8/check_15_8f.py`: (a) vs full_15_7j.xml with NEW = union of the `## New test ids` sections (junit ids,
       `tests.ta_r4.test_x::test_y`, one per line; any other line is STOP) and declared = union of the `## Declared spec
       updates` sections of the nine 15.8a–e SUMMARYs, parsed (a missing section is STOP; nothing typed); renames as
       declared; expect = base totals (read from full_15_7j.xml) + Σ N_new including this plan's 2 ids. (b) vs
       full_15_8e.xml: removed 0, added == this plan's 2 ids (passed), every other id identical. Arithmetic line in
       `$Q8/reconcile_15_8f.txt`. Any miss → STOP.
    3. HANDOFF (one script, `data/r4/tmp/w3f/handoff_edit.py` pattern): add `W3f158f_Q158AEIW_pending` ("15.8f stopped
       at Q-158AEIW; sentence sha256 <…> at $Q8/aeiw_sentence_15_8f.txt; cross-tab $Q8/aeiw_crosstab_15_8f.tsv; 15.8g
       inserts only after approval"); if any grch37_ref_match is undetermined, OPEN `W3f158_asthma_eur_grch37_fasta`
       ("<x_u> rows undetermined against 1000G Phase 3; deciding them needs a GRCh37 FASTA download — Carter");
       `resume_on_reconnect` = await Carter Q-158AEIW (orchestrator writes the reply and its sha256), then 15.8g;
       `suite_baselines_ta_r4_latest` = full_15_8f.xml counts. The W3f157_* keys are untouched (15.8g resolves them).
       Key count after == before + added; every pre-existing string value still present.
    4. PLAN-INDEX: 15.8f row `COMPLETE (ends at the Q-158AEIW STOP)`; add the 15.8g row (ta-r4-W3f-15-8-insert-review-and-close-PLAN.md,
       PLANNED, depends on 15.8f). STATE ★ RESUME HERE — LATEST ★ (NEXT = Carter Q-158AEIW, then 15.8g; NOT PUSHED); prior
       block SUPERSEDED. LOG entry (gate records; the identity sha256; contig check; symlink; the reference manifests and
       why checksum stays null; the data_sources.yaml append listed as a config/ta_r4 change that the W4a-T3 lock will
       hash; the lifted.bed join choice; the control sampling rule; the cross-tab; A/B green job id; NC results). SUMMARY with
       `## Declared spec updates`: none, and `## New test ids`: the 2 ids of <new_tests>, junit form.
    5. PINS (`pytest tests/m3/test_source_freeze_pins.py`); `git fsck --connectivity-only` before and after; commit
       `docs(ta-r4-W3f): 15.8f — asthma EUR reference measurement, FULL reconciled, records; stops at Q-158AEIW (no push)`,
       explicit paths. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8f.py && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import json,yaml;h=json.load(open('.planning/HANDOFF.json'));assert 'W3f158f_Q158AEIW_pending' in json.dumps(h);d=yaml.safe_load(open('config/ta_r4/decision_rules.yaml'));assert d['locked'] is False" && test -z "$(git status --porcelain -- .planning/HANDOFF.json .planning/STATE.md .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-review-suite-and-close-SUMMARY.md)" && git diff --quiet HEAD -- .planning/amendments/osf-amendment-r4-DRAFT.md</automated>
  </verify>
  <done>FULL 2,768 reconciled cumulatively and against 15.8e; records committed with explicit paths; HANDOFF points at Q-158AEIW then 15.8g; the DRAFT is unchanged; nothing pushed.</done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 4: STOP — Q-158AEIW, Carter approves or holds the filled DRAFT (c) sentence</name>
  <files>(none written by the executor; the orchestrator writes W3f-carter-15-8-Q-158AEIW-reply-<date>.txt)</files>
  <what-built>Measured per-row manifest, cross-tab, the 19-row table and the filled sentence (sha256 in `$Q8/aeiw_sentence_15_8f.sha256`). Precedent: Q-158KW and Q-158R7 approved public wording; "Disclose, no filter" (Q-158AEI) approved the policy, not this wording.</what-built>
  <action>
    1. Return the checkpoint with Q-158AEIW in the two-line format of <question> (line 1 with the sentence copied from
       the file, not retyped, and the two table paths with their sha256), and the tables for the orchestrator to show: the cross-tab for BOTH groups (flipped and unflipped control,
       with the control sampling rule and stratum population sizes),
       the 19-row table, the meaning of `undetermined` for each half, and the note that a GRCh37 FASTA download would be
       needed to decide GRCh37-undetermined rows. Options in the <question> order, `Hold — do not insert` first.
    2. Stops even under --auto / yolo / --chain; the executor selects nothing, writes no reply file and edits nothing.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && test -z "$(ls .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158AEIW-reply-*.txt 2>/dev/null)" && git diff --quiet HEAD -- .planning/amendments/osf-amendment-r4-DRAFT.md</automated>
  </verify>
  <done>The question is presented; no reply file was written by the executor; 15.8f is complete. The orchestrator writes Carter's reply, states its sha256, and starts 15.8g.</done>
  <resume-signal>Orchestrator: Carter's reply file written and its sha256 stated → 15.8g. `Hold — do not insert` → nothing is inserted; 15.8g does not run until Carter re-decides.</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| planner prose → public text | an unmeasured explanation entered a Carter question; only measured counts and Carter's approval of the filled text may cross (in 15.8g) |
| external reference files → measurement | unpinned /rs1 files; pinned by sha256 and reached by registered repo-relative paths |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-158f-01 | Tampering | reference files | mitigate | house-format sha256 manifests; test A re-checks size + sha256 of every file opened; NC (vi) |
| T-r4-158f-02 | Tampering | causal premise in the sentence | mitigate | four tri-state columns, cross-tab flipped vs unflipped control × class × |ΔEAF| group; sentence prints counts only; Carter approves before insertion |
| T-r4-158f-03 | Tampering | diagnostic module drifting from the 15.8a2 manifest | mitigate | byte rebuild (STOP on difference); NC (ii); referenced by nothing in the analysis path |
| T-r4-158f-04 | Elevation | auto-mode approving AEIW | mitigate | first option non-approving; executor never writes the reply; orchestrator states its sha256 |
| T-r4-158f-05 | Information disclosure | push / OSF | accept | none in 15.8 |
</threat_model>

<verification>
- Gates and tracked-file checks pass; the module's byte identity holds and it is the only src change; both references
  verified and pinned; tests A and B green in their own sbatch run with every NC failing; FULL 2,768 reconciled;
  records committed; Q-158AEIW presented with `Hold — do not insert` first; DRAFT unchanged; decision_rules.yaml locked
  false; n_regions_min 7.
</verification>

<success_criteria>
- Carter can decide the (c) wording from measured counts that distinguish a lift-changed reference from a by-construction
  mismatch, with every reference pinned and nothing inserted before his approval.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-review-suite-and-close-SUMMARY.md`
</output>
