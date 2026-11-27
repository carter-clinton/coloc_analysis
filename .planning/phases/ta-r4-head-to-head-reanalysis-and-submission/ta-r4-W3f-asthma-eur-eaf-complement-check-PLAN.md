---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8f2
slug: W3f-asthma-eur-eaf-complement-check
type: execute
wave: 15.8f2
depends_on: ["ta-r4-W3f-15-8-review-suite-and-close"]
gap_closure: true
files_modified:
  - .planning/DECISIONS.md                                                                                       # Q-158AEIW DEC
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158AEIW-reply-2026-11-27.txt   # orchestrator-written, committed as received
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-asthma-eur-eaf-complement-check-PLAN.md  # this plan, committed in Task 1
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-insert-review-and-close-PLAN.md      # frontmatter depends_on + hold note only
  - src/python/ta_r4/orientation_eaf.py                                                                           # additive diagnostic functions only (carve-out)
  - tests/ta_r4/test_asthma_eur_eaf_complement.py                                                                 # new; tests D and E
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/asthma_eur_gbmi_raw_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_complement.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_complement_crosstab.tsv
  - .planning/HANDOFF.json
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-asthma-eur-eaf-complement-check-SUMMARY.md
autonomous: false
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Every gate of 15.8f Task 1 step 1 passes again (gate_157j.sh; gate_158.sh with the ten QIDs; gate_158r2.sh; gate_158a2.sh Q-158OR Q-158PAL Q-158EL; the tracked-file checks), and Q-158AEIW, added to gate_158.sh by full file name (`F[]`, question `sed`-copied from line 1), passes with sha256 c06539ae941b756927a4567d7a522c67d73527796c7bf7af2fb454910e63ae2e and label `Hold — do not insert`; its `tail -n 1` == `Carter reply (verbatim, selected option): Hold — do not insert`; its three NCs exit 2"
    - "DEC-2026-11-27-ta-r4-asthma-eur-eaf-sentence-held quotes the Q-158AEIW reply with `cat` between ```text fences, the quote extracted back is `cmp`-equal to the reply file, the rest of DECISIONS.md is byte-equal to the pre copy; every number in the DEC is read by the script from data/r4/tmp/w3f/q158/aeiw_crosstab_15_8f.tsv (sha256 ce4a15cf…b844, re-checked), and the orchestrator's hand check (16 of 19, 12 of 14 indels) is labelled as relayed context, not a measurement"
    - "15.8g's frontmatter depends_on == [\"ta-r4-W3f-15-8-review-suite-and-close\", \"ta-r4-W3f-asthma-eur-eaf-complement-check\"] and a <hold_note> block states that its (c) sentence is withdrawn and must be re-filled and re-approved; `git diff --numstat` of that file is exactly 1 deletion and the note's added lines; PLAN-INDEX has a 15.8f2 row and the 15.8g row says it depends on 15.8f2"
    - "Pattern rule pinned in the module and used everywhere: agree iff |EAF − EAF_ref| ≤ AGREE_TOL (0.1); complement iff |EAF + EAF_ref − 1| ≤ COMPLEMENT_TOL (0.1) and |EAF − EAF_ref| > DELTA_MIN (0.2); other otherwise; unavailable if either EAF is missing or non-numeric; agree is tested first; floats parsed from the file strings, no rounding; eaf_pattern takes agree_tol and complement_tol as separate arguments; sensitivity with both set to 0.05 and to 0.15 (|ΔEAF| > 0.2 fixed) reported beside the primary 0.10; test E asserts the constants' values"
    - "The join covers ALL asthma EUR oriented rows in the 31 windows with row_class ≠ absent and numeric EAF, flipped and unflipped, SNV / indel / palindromic SNV (palindromic rows are kept but reported only as their own class); n(class ≠ palindromic_SNV and pattern_t2d ≠ unavailable) reproduces the 15.8f aggregate exactly: flipped 225, unflipped 216,105 (read from manifests/sumstats_r4_orientation_eaf.tsv), and the 19 flipped rows above 0.2 split into complement 16 (12 indels + 4 SNVs, the 16 keys listed in <context>) and other 3 — any difference is STOP"
    - "Each asthma row carries an EAF and a pattern against each of t2d EUR, hypertension EUR, BMI EUR and stroke EUR (oriented files, sha256 vs sumstats_r4_sha256.tsv) and 1000 Genomes Phase 3 EUR_AF (pinned GRCh37 VCFs; exact allele key only, swapped key → 1 − EUR_AF, multi-allelic rules in <context>), and a symmetric verdict over the sources with an EAF: `<source>_outlier` iff ≥ 3 sources, that source is complement to every other and every pair of the others agrees; `all_agree`; `mixed`; `lt3_sources`; and verdict_with_1kg, the same outlier verdict counted only where 1000G is among the agreeing sources (else `outlier_without_1kg`), reported beside verdict with n_sources by class, because the four sumstats references are not independent (one project harmonizer; per the published study descriptions, not measured here, t2d, hypertension, BMI and GBMI asthma include UK Biobank); each reference's build and lift origin (data_sources.yaml build / lifted_from) is recorded"
    - "For the per-row rows the source chain is measured: GBMI raw (data/raw/region_analysis/sumstats/asthma.EUR.raw.gz, pinned in manifests/asthma_eur_gbmi_raw_sha256.tsv) → harmonized GRCh38 (by lifted.bed input line, 15.8f rule) → lifted → oriented, with REF/ALT/EAF carried or not at each step and GBMI's own is_strand_flip / is_diff_AF_gnomAD; every indel of the join gets indel_kind, anchored, left_aligned_grch38 and in_repeat_grch38 (tri-state) by the rules in <context>, cross-tabbed against its pattern"
    - "Exposure is read from stored inputs and outputs only (no fit run, no LD read): per region the complement and outlier counts; the production fit keys (measure_fit_eligibility.fit_keys) with trait asthma or t2d, EUR, and their eligibility in manifests/w3f_fit_eligibility.tsv; the admissible pair_manifest rows that pair asthma EUR with another trait; the path each EUR arm reads (paths.sumstats_path); whether each outlier row's key is in each production fit key's variant set (r4 catalog ∩ the arm's fit panel, by key); and, for every asthma EUR and t2d EUR RDS in manifests/prelock_pilot_fits.tsv, whether any complement or outlier row is a credible-set member, by names only (colnames(fit$lbf_variable) and fit$sets$cs; no pip, alpha, mu or lbf value is read, checked by R getParseData symbols with an NC), resolved by allele key with variant_match.R resolve_fit_names as 15.8e did; the pilot script writes only (fit_path, member_key); regions_r4.csv lead_snp is reported only as region_lead_snp (a pre-registered region definition) and the word \"lead\" never appears in the findings"
    - "Two committed manifests in house format (line 1 column header, tab, no comment line): the per-row manifest (every joined row with |ΔEAF| > 0.2 against at least one source) and the cross-tab (table, group, class, stratum, reference, value, n, denominator; every n has its denominator); the GBMI raw pin in house reference format (`rel_path\\tsize_bytes\\tsha256\\tsource`)"
    - "orientation_eaf.py changes are additive only: `git diff --numstat <start> HEAD -- src` == one line for src/python/ta_r4/orientation_eaf.py with 0 deletions, numstat is exactly one line; every top-level function and constant present at start has an identical ast.get_source_segment at HEAD; no new top-level name collides with a start name; every new top-level statement is a def or an assignment to a new UPPER_CASE constant; no module-level call (checked by script; its NC, a redefinition of ref_match, fails), and render_eaf_manifest(eaf_diffs()) still has sha256 7ad5ce50…80c0; nothing in src, workflow, Snakefile* or config references it"
    - "Tests D (r4_heavy) and E (quick) are RED before the code and GREEN in one dedicated sbatch run (cascadelake; junit parsed); every NC (in-place mutation of the file the test reads, restored by copy, sha256-equal after; PYTHONDONTWRITEBYTECODE=1) makes its test fail"
    - "FULL under Slurm (cascadelake, --mem=96G, -t budgeted from test D's measured time) reconciled per id against full_15_7j.xml over the ten 15.8a–f SUMMARYs plus this plan's 2 ids (2,694 + 72 + 2 + 2 = 2,770 = 2,717 P / 53 S / 0 F; read from the SUMMARYs, not typed) and against full_15_8f.xml: identical by id except exactly this plan's 2 added ids, each passed"
    - "15.8f2 ends at a blocking STOP, Q-158EAFC, after its records are committed: options in order `Hold` / `Disclose only` / `Treat as a data defect: plan a correction` / `Other`, none labelled Recommended; the executor states its recommendation in the question line from the pre-stated rule in <question>; the orchestrator writes the reply file and states its sha256; the executor never writes or answers it"
    - "No production code, catalog, sumstats, panel or fit changes; no DRAFT edit; decision_rules.yaml locked: false; n_regions_min 7; no push, OSF, fit or W4a-T3 lock; Slurm only; explicit paths only in every commit"
  artifacts:
    - path: "src/python/ta_r4/orientation_eaf.py"
      provides: "15.8f module plus additive complement-check functions"
      exports: ["AGREE_TOL", "COMPLEMENT_TOL", "DELTA_MIN", "SENSITIVITY_TOLS", "EUR_REFERENCES", "eaf_pattern", "verdict", "verdict_with_1kg", "onekg_eaf", "indel_form", "left_aligned", "in_repeat", "all_rows", "input_fields", "raw_fields", "complement_rows", "render_complement_manifest", "render_complement_crosstab"]
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_complement.tsv"
      provides: "every joined asthma EUR row with |ΔEAF| > 0.2 against at least one source; patterns, verdict, source chain, indel form, exposure columns"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_complement_crosstab.tsv"
      provides: "counts with denominators over ALL joined rows"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/asthma_eur_gbmi_raw_sha256.tsv"
      provides: "GBMI asthma EUR raw file pin"
    - path: "tests/ta_r4/test_asthma_eur_eaf_complement.py"
      provides: "tests D and E"
  key_links:
    - from: "tests/ta_r4/test_asthma_eur_eaf_complement.py"
      to: "src/python/ta_r4/orientation_eaf.py"
      via: "import; byte rebuild of both complement manifests"
      pattern: "from ta_r4 import orientation_eaf"
    - from: "Q-158EAFC question line"
      to: "manifests/sumstats_r4_orientation_eaf_asthma_eur_complement_crosstab.tsv"
      via: "every number filled by script from the cross-tab; sha256 stated"
      pattern: "Q-158EAFC"
---

<objective>
Carter held the filled DRAFT (c) sentence (Q-158AEIW `Hold — do not insert`). Record that, then measure whether the
asthma EUR rows whose effect-allele frequency disagrees with the EUR type 2 diabetes file show a complement pattern
(EAF + EAF_ref ≈ 1), across ALL joined rows and against four more references, so that the file attaching the
frequency to the other allele can be identified. Then locate the stage where it happens, describe the indel
representation, and measure exposure in production fit keys and pre-lock pilot fits. Measurement only. The plan ends at
the blocking Q-158EAFC STOP.
Output: AEIW DEC; 15.8g held behind 15.8f2; GBMI raw pin; additive module functions; per-row and cross-tab manifests;
tests D and E with NCs; FULL reconciled; records; the Q-158EAFC question. No DRAFT edit. No push.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
All replies of 15.8f's <question> are re-gated exactly as there (Q-157J; the five 2026-11-25 replies; Q-158R2, Q-158OR,
Q-158PAL, Q-158EL; Q-158R6G (both files), Q-158KW, Q-158DFX, Q-158AEI, Q-158AEIM with their tracked-file checks;
Q-158AEIM is now tracked, added in 456ae994).

Q-158AEIW (answered; gated and recorded here):
| QID | file | sha256 | label | tracked |
|---|---|---|---|---|
| Q-158AEIW | `W3f-carter-15-8-Q-158AEIW-reply-2026-11-27.txt` | `c06539ae941b756927a4567d7a522c67d73527796c7bf7af2fb454910e63ae2e` | `Hold — do not insert` | untracked; committed in Task 1 step 3 |
Its question text = line 1 after `Question Q-158AEIW (2026-11-27): `, copied by `sed`, never retyped. Its last line is
asserted with `tail -n 1`. Its two table sha256 values (ce4a15cf…b844, b21e4235…cc54) are re-checked against the files.

Q-158EAFC (this plan's question, asked at the Task 4 STOP). The reply file has exactly two lines:
- line 1: `Question Q-158EAFC (<YYYY-MM-DD>): asthma EUR effect-allele frequency complement check (15.8f2), measured
  after your Q-158AEIW Hold. <$Q8/eafc_findings_15_8f2.txt, verbatim, inline> <$Q8/eafc_recommendation_15_8f2.txt,
  verbatim, inline> What next? Tables: .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_complement_crosstab.tsv
  sha256 <…>; .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_complement.tsv sha256 <…>`
  (the two values from `$Q8/eafc_tables_15_8f2.sha256`);
- line 2: `Carter reply (verbatim, selected option): <label>`, or for Other `Carter reply (verbatim): <text>`
  (gate_reply.py's free-text form, gated with `--free-text <text>`; Task 1 confirms gate_reply.py accepts it by a dry
  run on a scratch reply in a tmp `--dir`, rc 0, and rejects a mismatching text, rc 2).
Options, in this order (yolo / auto-advance selects the FIRST option at a blocking gate, so the first is non-approving):
`Hold` / `Disclose only` (a new sentence, drafted later and approved in its own question) / `Treat as a data defect:
plan a correction` (a new plan, not this one) / `Other`. No option is labelled Recommended.

Findings text (`$Q8/eafc_findings_15_8f2.txt`, one line, written by script from the cross-tab; numbers never typed;
every numerator printed with its denominator; all counts printed even when 0; no causal word such as "because",
"error", "mislabelled", "defect", and no word "lead" — asserted by a word list in the script):
`Against the EUR type 2 diabetes file, <c> of <n> joined asthma EUR rows have complementary frequencies (|EAF + EAF_ref
− 1| ≤ 0.1 with |ΔEAF| > 0.2): <c_f> of <n_f> flipped (<c_fi> of <n_fi> indels) and <c_u> of <n_u> unflipped (<c_ui> of
<n_ui> indels); palindromic SNVs, reported apart, <c_p> of <n_p>. Complement / rows with an EAF against the other
sources: hypertension <..> / <..>, BMI <..> / <..>, stroke <..> / <..>, 1000 Genomes EUR (exact allele key) <..> /
<..>. Of the <v_n> complement-vs-type 2 diabetes rows with at least three sources, the asthma file is the outlier at
<v_a> (<v_ai> indels), the type 2 diabetes file at <v_t>, another source at <v_o>; all agree at <v_g>, mixed <v_m>;
<v_lt3> have fewer than three sources. Counted only where 1000 Genomes is among the agreeing sources: asthma outlier
at <w_a>, type 2 diabetes outlier at <w_t> (<w_x> outlier rows have no 1000 Genomes frequency). The four sumstats
references are not independent: all four passed through this project's harmonizer, and, per the published study
descriptions (not measured here), the type 2 diabetes, hypertension and BMI files include UK Biobank, as does the GBMI
asthma file. Tolerance 0.05 / 0.15: asthma outlier at
<v_a05> / <v_a15>. Of the <v_a>
asthma-outlier rows, <k_raw> are in the GBMI raw file with the same alleles and the same frequency as our GRCh38 input
(<k_raw_x> are not), GBMI flags is_diff_AF_gnomAD at <k_gn> of them and is_strand_flip at <k_sf>; <i_ins> are
insertions and <i_del> deletions, <i_rep> in a repeat (indels of the whole join: <I_ins> / <I_del>, <I_rep> in a
repeat). They fall in <x_r> of the 31 windows; <x_k> of the <x_K> production asthma EUR fit keys cover such a window
(<x_e> eligible) and <x_v> have such a row in their variant set; they are credible-set members at <x_m> rows in <x_f>
of the <x_F> asthma EUR pre-lock pilot fits. The <v_t> type 2 diabetes-outlier rows fall in <y_r> windows; <y_k> of the
<y_K> production t2d EUR fit keys cover such a window (<y_e> eligible) and <y_v> have such a row in their variant set;
they are credible-set members at <y_m> rows in <y_f> of the <y_F> t2d EUR pre-lock pilot fits.`
If v_a == 0 the asthma-outlier clauses print 0 and are kept (never dropped).

Recommendation (`$Q8/eafc_recommendation_15_8f2.txt`, one line, rule fixed here before measurement; the executor
reports which branch fired and the counts it used; Carter decides):
1. If fewer than half of the complement-vs-t2d rows have ≥ 3 sources (v_n < c / 2) → `The executor recommends Hold:
   at <c − v_n> of <c> rows the measurement cannot tell the files apart.`
2. Else, if for some source S ∈ {asthma, t2d} at least one row R meets all three of (i) verdict_with_1kg ==
   `<S>_outlier` (1000G agrees with the other sources), (ii) R's key is in the variant set (r4 catalog ∩ fit panel) of
   a production fit key of S's trait, (iii) in_repeat_grch38 ≠ true → `The executor recommends Treat as a data
   defect: plan a correction: <S> is the outlier with 1000 Genomes agreeing at <n_S1> rows, <n_Sv> of them in the
   variant set of <n_Sk> production fit keys, <n_Svr> of those in a repeat.` If both asthma and t2d meet it, the line
   names both files, each with its own counts. The repeat share (n_Svr of n_Sv) is always printed.
3. Else → `The executor recommends Disclose only: no outlier row with 1000 Genomes agreeing lies outside a repeat in the
   variant set of a production fit key (<n_a1> asthma and <n_t1> type 2 diabetes outlier rows with 1000 Genomes
   agreeing; <n_av> / <n_tv> in a variant set, <n_avr> / <n_tvr> of those in a repeat).`
The ORCHESTRATOR writes the reply byte-for-byte as `W3f-carter-15-8-Q-158EAFC-reply-<YYYY-MM-DD>.txt` and states its
sha256 in the next resume message. The executor never writes, answers or edits it.
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-review-suite-and-close-PLAN.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-review-suite-and-close-SUMMARY.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158AEIW-reply-2026-11-27.txt
@data/r4/tmp/w3f/q158/multikey_15_8e.R

`$Q8` = data/r4/tmp/w3f/q158. Start SHA 02d11967 expected (`git rev-parse HEAD > $Q8/start_15_8f2.txt`; if HEAD
differs, record it and check that `git diff --name-only 02d11967 HEAD` touches none of this plan's inputs, else STOP).

**Standing rules:** 15.8 shared protocol (15.8a `<protocol>`); memories feedback_a_test_must_discriminate_between_hypotheses
(symmetric verdict; agree rows as a control), feedback_aggregate_agreement_hides_component_errors (the 16 keys are
checked one by one, not as a count), feedback_green_assertion_needs_a_negative_control,
feedback_negative_control_defeated_by_bytecode_cache, feedback_gsd_automode_bypasses_blocking_fire_gates (EAFC option
order), feedback_a_count_is_a_claim_scope_and_reconcile (every n reconciled against its denominator and, where one
exists, an independent recount), feedback_grep_gate_matches_text_not_meaning (pins by ast / exit code, not grep),
feedback_slurm_not_lsf (`sbatch -p compute -A clintonlab_cpu -q normal -t …`, RSCRIPT by absolute path:
/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript).

**Measured so far (15.8f; read from aeiw_crosstab_15_8f.tsv and aeiw_rows_15_8f.tsv, both sha256-checked).**
lift_changed_ref true: flipped indels above 0.2: 0 of 14 (9 false, 5 undetermined); flipped indels at or below 0.2:
0 of 7; flipped SNVs above 0.2: 1 of 5; flipped SNVs at or below 0.2: 196 of 199; unflipped control: 0 of 4,525.
So the lift accounts for most flipped SNVs at or below 0.2 and for none of the high-ΔEAF indels.
**Relayed by the orchestrator (hand check, not yet a measurement; Task 2 measures it):** 16 of the 19 flipped rows
above 0.2 (12 of the 14 indels) have |EAF + EAF_t2d − 1| < 0.1. Planner re-count from aeiw_rows_15_8f.tsv at ≤ 0.1
gives the same 16. Complement (lifted-source CHR:POS:REF:ALT): 5:73331273:G:GA, 19:44993876:AAAAT:A,
19:45050993:G:A, 19:45062119:T:TA, 19:45413224:T:TG, 19:45704460:C:CA, 19:45717714:GTGTT:G, 6:27447988:A:AAAATAAAT,
6:28853839:G:GT, 6:30689377:C:CG, 6:31351593:G:A, 6:31351594:C:T, 6:32589938:G:A, 6:33818581:AC:A, 6:495127:C:CT,
2:202704386:T:TAGACAGAC. Other: 19:44993639:G:A, 6:32948598:A:AC, 11:21658477:A:AATGAT. 6:495127 sits at 0.098,
near the tolerance, which is why the sensitivity tolerances are reported. Noted, not interpreted: the 4 complement
SNVs have grch38_ref_match false in 15.8f; the non-complement SNV has it true.
Example (5:73331273): oriented asthma GA/G EAF 0.993201 (of G); lifted source G/GA EAF 0.006799 (of GA), so the flip is
consistent; t2d.EUR.r4_oriented GA/G EAF 0.0151 (of G); 1000G has no record at 73331273 (planner tabix, 2026-11-27).

**Hypotheses the measurement must separate.** H-asthma: the asthma file attaches the frequency (and possibly the
effect) to the other allele at these rows. H-reference: the t2d file does. H-representation: the two files describe
different events with the same allele strings (for example an insertion vs a deletion in a repeat), so neither label is
wrong but the keys do not denote the same allele. Only a third and fourth source can separate H-asthma from
H-reference, so the verdict is symmetric (any source can be the outlier). H-representation predicts outliers enriched in
repeats and among `onekg_match == none`, which the indel table shows. EAF alone cannot show which allele BETA refers
to; the question line says frequency, never effect.

**EAF convention.** sumstats_orient.HEADER column EAF is the frequency of ALT (config/datasets.yaml gbmi_asthma:
ALT ← ALT, EAF ← all_meta_AF); 1000G EUR_AF is per ALT (`Number=A`). Every EAF here is the frequency of the row's
ALT in the orientation stated; the pattern compares files at the same oriented key.

**Rules (module constants; units in the file's EAF scale).**
- `AGREE_TOL = 0.1`, `COMPLEMENT_TOL = 0.1`, `DELTA_MIN = 0.2`, `SENSITIVITY_TOLS = (0.05, 0.10, 0.15)` (sensitivity
  sets agree_tol = complement_tol = t; DELTA_MIN fixed). `eaf_pattern(e, r, agree_tol=AGREE_TOL,
  complement_tol=COMPLEMENT_TOL)`: None in either → `unavailable`; |e − r| ≤ agree_tol → `agree`; |e + r − 1| ≤
  complement_tol and |e − r| > DELTA_MIN → `complement`; else `other`.
- `EUR_REFERENCES = (("t2d","EUR"), ("hypertension","EUR"), ("bmi","EUR"), ("stroke","EUR"))`, files
  `so.oriented_path(t, a)`, keyed per window by `norm_key(*f[:4])` → EAF as `_join` does (last row wins on a duplicate
  key, the 15.8a2 rule kept for the identity; the number of joined rows whose key is duplicated in each reference
  window is written to the cross-tab table `duplicate_reference_key`). Each reference also records `class_<t>` =
  `so.row_class` of that reference's own catalog-source row (was the reference row itself flipped). Provenance per
  reference (cross-tab table `reference_provenance`, LOG): data_sources.yaml `name`, `build` and `lifted_from` (planner
  2026-11-27: all four build GRCh37, no `lifted_from`; asthma EUR lifted_from the GRCh38 harmonized file), and
  whether a raw file exists under data/raw/region_analysis/sumstats (planner: bmi, hypertension, stroke EUR yes; t2d
  no). Independence: all four passed through the project harmonizer (data/processed/sumstats_harmonized); and, per the
  published study descriptions (not measured here), the type 2 diabetes, hypertension and BMI files include UK
  Biobank, as does the GBMI asthma file (cited: GBMI, Zhou et al. 2022; DIAMANTE 2022; Evangelou 2018; Yengo 2018; the
  LOG names these four sources). Agreement among them is therefore not independent confirmation, which is why
  verdict_with_1kg is reported.
- `all_rows(repo, tabix)`: every asthma EUR oriented row of the 31 windows with `row_class ≠ absent` and numeric EAF,
  in `_join` order; `group` flipped iff `swapped_only`; `class` = `palindromic_SNV` if `so.is_palindromic(REF, ALT)`,
  else `SNV` iff len(REF) == len(ALT) == 1, else `indel`.
- `onekg_eaf(ref, alt, records)`: records = (POS, REF, ALT list, EUR_AF list) of the 1000G VCF lines at the row's POS,
  read once per window (`tabix chr<C>.vcf.gz <C>:start-end`, 23 → X), symbolic ALTs (`<…>`) ignored. Exact: VCF REF ==
  ref and alt ∈ ALT[i] → EUR_AF[i]; swapped: VCF REF == alt and ref == ALT[i] → 1 − Σ EUR_AF (frequency of the VCF
  REF); more than one record matching (either way) → `ambiguous`, EAF None; none → `none`, EAF None; a missing or
  `.` EUR_AF → `no_af`, EAF None. Returns (onekg_match, EAF). No normalization, no nearby matching for the EAF.
  `onekg_nearby_indel` (indels with `none` only): any non-symbolic 1000G record within [POS − 20, POS + len(REF) + 20]
  whose |len(REF) − len(ALT[i])| equals the row's → true / false.
- `verdict(eafs)`: eafs = {source: EAF or None} over asthma + the five references. Sources with an EAF = A. |A| < 3 →
  `lt3_sources`; all pairs agree → `all_agree`; exactly one S complement to every other source and every pair of the
  others agree → `<S>_outlier`; else `mixed`. Pairs use `eaf_pattern` with the same tolerances. Palindromic rows get a
  verdict but are only reported as their own class. `verdict_with_1kg(eafs)` = verdict(eafs) if it is not an outlier
  verdict; for `<S>_outlier` it is `<S>_outlier` iff S ≠ 1kg and 1kg has an EAF (so 1kg is among the agreeing
  sources), else `outlier_without_1kg`.
- Indel form (every indel of the join, on the lifted-source REF/ALT, which are the GRCh38 REF/ALT for every indel since
  minus-strand non-SNVs were dropped by script_used.sh): `indel_kind` = insertion if len(ALT) > len(REF), deletion if
  shorter; `anchored` = (min(len) == 1 and REF[0] == ALT[0]); S = longer[1:]. `left_aligned_grch38` (anchored and
  grch38_ref_match true only, else undetermined): true iff REF[0] ≠ S[-1] (no left shift possible). `in_repeat_grch38`
  (anchored only, else undetermined; GRCh38 bases via grch38_bases, None → undetermined): insertion: bases
  [POS38 + 1, POS38 + len(S)] == S; deletion: bases [POS38 + len(REF), POS38 + len(REF) + len(S) − 1] == S.
- Source chain (per-row rows; GRCh38 row through `grch38_rows` by lifted.bed input line, 15.8f rule; `input_fields`
  reads those input lines of data/processed/sumstats_harmonized/asthma.EUR.tsv.bgz in one pass): `raw_fields` streams
  data/raw/region_analysis/sumstats/asthma.EUR.raw.gz once (gzip; header asserted == `#CHR POS REF ALT rsid
  all_meta_AF inv_var_meta_beta inv_var_meta_sebeta inv_var_meta_p inv_var_het_p direction N_case N_ctrl n_dataset
  n_bbk is_strand_flip is_diff_AF_gnomAD`, else STOP) and keeps rows whose (CHR, POS) is a wanted GRCh38 position;
  `raw_match` = exact (one raw row with REF/ALT == the GRCh38 input REF/ALT) / swapped / multiple / absent;
  `chain_eaf_kept` = float(all_meta_AF) == float(input EAF) (tri-state: undetermined unless raw_match exact);
  lifted vs input: alleles equal on `+`, complements on `-` (15.8f); oriented vs lifted: swapped with EAF = 1 − EAF on
  flipped rows, equal on unflipped (`verify_unflip` semantics; any row failing = STOP, it would contradict 15.8a2).
  Columns raw_is_strand_flip and raw_is_diff_AF_gnomAD copied as written.

**Exposure (stored inputs and outputs only).** Production fit keys = `measure_fit_eligibility.fit_keys()` filtered to
(trait ∈ {asthma, t2d}, ancestry EUR); eligibility = the `eligible` column of manifests/w3f_fit_eligibility.tsv for the
same (arm, trait, ancestry, region_safe) (absent → `not_listed`). Pairs = the admissible pair_manifest rows
(`measure_fit_eligibility._manifest()`) with asthma EUR or t2d EUR as trait_a or trait_b. Arm paths =
`paths.sumstats_path(trait, "EUR", arm)` for every arm with EUR in `arms.arm_ancestries(arm)`. Pilot fits: every
`kind == rds` row of manifests/prelock_pilot_fits.tsv (line 1 comment skipped) with trait asthma or t2d and ancestry EUR
(count printed; read, not typed). `$Q8/eafc_pilot_15_8f2.R`, written from multikey_15_8e.R, names only (orchestrator
decision 2026-11-27): per fit, members = `unique(colnames(fit$lbf_variable)[unlist(fit$sets$cs)])`; it reads nothing
else from the fit object. Before it runs, `$Q8/eafc_pilot_parse_check_15_8f2.R` walks `getParseData(parse(<script>,
keep.source = TRUE))`: no SYMBOL, SYMBOL_FUNCTION_CALL or STR_CONST token equals pip, alpha, mu, mu2, lbf, V, KL,
elbo or sigma2, where STR_CONST text is compared after stripping its enclosing quotes (getParseData keeps them, so
`fit[["alpha"]]` appears as `"alpha"`; strip one leading and trailing `"` or `'`, and for raw strings the r"(…)" wrapper); `lbf_variable` occurs exactly once, as the `$` field inside a `colnames(...)` call (parent chain); NC:
a scratch copy with `x <- fit$pip` appended fails the check, and one with `fit[["alpha"]]` fails it. Names
resolved with variant_match.R `resolve_fit_names` (no --allow-duplicate-rows) through the sumstats file the
fit's JSON records (sha256 vs sumstats_r4_sha256.tsv; a recorded file with no pin is counted `sumstats_unpinned` and not
resolved), the r4 catalog and the EUR_1kg_r4 fit panel as 15.8e did; it writes only `$Q8/eafc_pilot_members_15_8f2.tsv`
whose line 1 is asserted == `fit_path\tmember_key` exactly and whose rows have two fields. A complement / outlier row is a member if its lifted-source key, its swap, or (for
a fit reading the GRCh38 file) its GRCh38 key equals a resolved member key; never by position alone. Positive control:
the first resolved member of asthma.EUR.FTO_16q12 (A3_1kg_newcat) in multikey_15_8e.tsv added to the query keys is
reported as a member, then removed. Variant sets: for each production fit key, the row's oriented key ∈ the r4
catalog of the region (`paths.catalog_path("r4", region_safe)`, sha256 vs catalogs_r4_fixed_point.tsv) and ∈ the
arm's fit panel variants (read as multikey_15_8e.R reads EUR_1kg_r4's; a panel whose variant list cannot be found is
STOP), by normalized key only. Column region_lead_snp = `regions_r4.csv` lead_snp (a pre-registered region definition)
equal to the row's SNP_ID (empty SNP_ID → counted `no_snp_id`). No LD file, no fit and no cs_cross_purity.R are run
or read.

**Forbidden:** any edit to production code, catalogs, sumstats, panels or fits; any edit to a pre-existing function or
constant of orientation_eaf.py; any DRAFT edit; any 15.8g edit beyond depends_on and the hold note; removing any
HANDOFF string; any new download (a GRCh37 FASTA stays Carter's call: HANDOFF W3f158_asthma_eur_grch37_fasta stays
OPEN). **Carve-out:** additive functions in src/python/ta_r4/orientation_eaf.py under 15.8f's rules (returns data;
manifests written by a `$Q8` driver; tool and reference paths are arguments; no /rs1, /share or /gpfs_common literal;
no import of tests; referenced by nothing in src, workflow, Snakefile* or config).
</context>

<interfaces>
From src/python/ta_r4/orientation_eaf.py (15.8f; use, do not modify):
```python
REF; TRUE, FALSE, UND = "true", "false", "undetermined"
def _join(repo, tabix, only=None)          # yields (t, a, cls, ref_file, rs, fs, fo, v, raw, delta); skips absent,
                                           # palindromic, non-numeric EAF on either side
def eaf_diffs(repo, tabix) -> dict; def render_eaf_manifest(diffs) -> str   # sha256 7ad5ce50…80c0
def eaf_rows(repo, tabix, trait, anc, cls) -> list[dict]
def grch38_rows(rows, input_bgz, lifted_bed) -> list[dict]   # input_line, strand, CHR_GRCh38, POS_GRCh38, REF_GRCh38, ALT_GRCh38
def grch38_bases(chrom, pos, length, fasta, samtools) -> str | None
def grch37_bases(chrom, pos, length, vcf_dir, tabix) -> str
def ref_match(ref, bases) -> str; def k_and(a, b) -> str; def k_not(a) -> str
```
From src/python/ta_r4/sumstats_orient.py: `HEADER`, `CATALOG_SOURCES`, `oriented_path`, `windows`,
`catalog_keys_by_region`, `row_class`, `is_palindromic`. From collector_drop_audit.py: `norm_key`. From
measure_fit_eligibility.py: `fit_keys(repo)`, `_manifest(repo)`. From arms.py: `ARMS`, `arm_ancestries`. From paths.py:
`sumstats_path(trait, anc, arm)`.

New (additive; repo-relative paths under `repo`; tools and references as arguments):
```python
AGREE_TOL = 0.1; COMPLEMENT_TOL = 0.1; DELTA_MIN = 0.2; SENSITIVITY_TOLS = (0.05, 0.10, 0.15)
EUR_REFERENCES = (("t2d", "EUR"), ("hypertension", "EUR"), ("bmi", "EUR"), ("stroke", "EUR"))
def eaf_pattern(e: float | None, r: float | None, agree_tol: float = AGREE_TOL, complement_tol: float = COMPLEMENT_TOL) -> str
def verdict(eafs: dict[str, float | None], agree_tol: float = AGREE_TOL, complement_tol: float = COMPLEMENT_TOL) -> str
def verdict_with_1kg(eafs: dict[str, float | None], agree_tol: float = AGREE_TOL, complement_tol: float = COMPLEMENT_TOL) -> str
def onekg_eaf(ref: str, alt: str, records: list[tuple[int, str, list[str], list[str]]]) -> tuple[str, float | None]
def indel_form(ref: str, alt: str) -> dict          # indel_kind, anchored, S
def left_aligned(ref: str, alt: str, anchor_match: str) -> str
def in_repeat(ref, alt, pos38, fasta, samtools) -> str
def all_rows(repo, tabix, vcf_dir) -> list[dict]    # the join of <context>, EAF_<t> / class_<t> per reference, EAF_1kg, onekg_match
def input_fields(input_bgz: str, lines: set[int]) -> dict[int, list[str]]
def raw_fields(raw_gz: str, positions: set[tuple[str, int]]) -> dict
def complement_rows(rows, grch38, inputs, raw, fasta, samtools, exposure) -> list[dict]   # per-row manifest rows
def render_complement_manifest(rows) -> str
def render_complement_crosstab(all_rows, per_row, exposure) -> str
```
Per-row manifest columns (line 1, in order): region_safe CHR POS SNP_ID REF ALT REF_oriented ALT_oriented group class
EAF EAF_t2d EAF_hypertension EAF_bmi EAF_stroke EAF_1kg onekg_match onekg_nearby_indel class_t2d class_hypertension
class_bmi class_stroke pattern_t2d pattern_hypertension pattern_bmi pattern_stroke pattern_1kg n_sources verdict
verdict_with_1kg verdict_tol_0.05 verdict_tol_0.15 indel_kind anchored left_aligned_grch38 in_repeat_grch38 input_line strand CHR_GRCh38
POS_GRCh38 REF_GRCh38 ALT_GRCh38 EAF_GRCh38 raw_match raw_all_meta_AF raw_is_strand_flip raw_is_diff_AF_gnomAD
chain_eaf_kept region_lead_snp n_prod_fit_keys_asthma n_prod_fit_keys_t2d n_prod_variant_sets_asthma
n_prod_variant_sets_t2d. EAF values written as read (strings);
EAF_1kg `repr(float)`; missing = empty field.
Cross-tab columns: table group class stratum reference value n denominator. Tables: `pattern` (group × class ×
reference × value; stratum `all`, and `>0.2` / `<=0.2` by |ΔEAF_t2d| for the 15.8f identity), `pattern_tol_0.05`,
`pattern_tol_0.15`, `verdict`, `verdict_with_1kg`, `n_sources` (group × class × value = number of sources),
`reference_provenance` (reference × value = name / build / lifted_from / raw_file), `verdict_tol_0.05`,
`verdict_tol_0.15`, `indel_form` (stratum =
`<indel_kind>|anchored=<…>|left_aligned=<…>|in_repeat=<…>`, value = pattern vs t2d, and again vs 1kg),
`onekg_match` (group × class × value), `duplicate_reference_key`, `chain` (value = raw_match / chain_eaf_kept /
raw_is_diff_AF_gnomAD / raw_is_strand_flip values, stratum = verdict), `exposure_region` (stratum = region_safe),
`exposure_fit_key` (stratum = arm|trait|region_safe, value = eligible value; n = outlier rows in the window and,
separately, in the variant set), `exposure_pair`, `exposure_arm_path`
(value = the path), `exposure_pilot` (stratum = fit path, value member; from $Q8/eafc_pilot_members_15_8f2.tsv,
sha256 in the LOG). Every row's n ≤ denominator; within each (table, group, class, stratum, reference) the values sum
to the denominator (asserted, except the exposure tables, which are counts with their own stated denominators).
</interfaces>

<new_tests>
tests/ta_r4/test_asthma_eur_eaf_complement.py; 2 junit ids (no parametrize). Paths: references read from
data_sources.yaml (`onekg_phase3_vcf.url`, `grch38_fasta_mapdamage.url`); the raw path from
manifests/asthma_eur_gbmi_raw_sha256.tsv row 2; tool paths as in test_asthma_eur_eaf_disclosure.py.
- D. `test_asthma_eur_eaf_complement_manifests_rederive` (r4_heavy): (a) sha256 + size of every input opened: the five
  oriented EUR files and the harmonized input vs sumstats_r4_sha256.tsv, the 48 1000G files vs
  grch37_reference_sha256.tsv, the FASTA / .fai / lifted.bed vs grch38_reference_sha256.tsv, the raw file vs its
  manifest (line 1 == `rel_path\tsize_bytes\tsha256\tsource`); (b) both complement manifests rebuilt byte for byte;
  (c) identities read, never typed: n(class ≠ palindromic_SNV and pattern_t2d ≠ unavailable) per group == the asthma
  EUR flipped and unflipped n of manifests/sumstats_r4_orientation_eaf.tsv; the flipped `>0.2` t2d complement count == the count
  recomputed from the EAF / EAF_reference columns of manifests/sumstats_r4_orientation_eaf_asthma_eur_flipped.tsv with
  `eaf_pattern`, row by row (same keys); (d) render_eaf_manifest(eaf_diffs()) sha256 unchanged.
- E. `test_eaf_complement_rules_and_module_hygiene` (quick): `eaf_pattern` cases — (0.5, 0.55) agree; (0.5, 0.6)
  agree (float |Δ| = 0.09999999999999998 ≤ 0.1; the test prints it); (0.9, 0.12) complement; (0.58, 0.42) other
  (sum 1.0 but |Δ| 0.16 ≤ 0.2); (0.7, 0.45) other (|Δ| 0.25, sum 1.15); (None, 0.3) unavailable; (0.96, 0.12)
  complement at the default and other at agree_tol = complement_tol = 0.05; (0.5, 0.605) other at the default and
  agree at agree_tol 0.11. Constants asserted: AGREE_TOL == 0.1, COMPLEMENT_TOL == 0.1, DELTA_MIN == 0.2,
  SENSITIVITY_TOLS == (0.05, 0.10, 0.15). `verdict_with_1kg`: asthma outlier with 1kg agreeing → asthma_outlier;
  asthma outlier among t2d / hypertension / BMI only → outlier_without_1kg.
  `verdict`: asthma outlier with three sources; t2d outlier; all agree; mixed; two sources → lt3_sources.
  `onekg_eaf`: exact; swapped → 1 − Σ; multi-allelic exact uses its own EUR_AF; multi-allelic swapped → 1 − Σ; two
  matching records → ambiguous; symbolic ALT ignored; `.` → no_af. `indel_form` / `left_aligned` / `in_repeat` on a
  tmp FASTA (built and faidx-indexed in the test): left-aligned and not, insertion and deletion in and out of a repeat,
  unanchored → undetermined. Hygiene: the module still imports from an empty tmp cwd with no file written; ast has no
  /rs1, /share or /gpfs_common literal and no tests import.
Expected FULL for 15.8f2: full_15_8f.xml (2,768) + 2 = 2,770 = 2,717 P / 53 S / 0 F.
</new_tests>

<tasks>

<task type="auto">
  <name>Task 1: gates incl. Q-158AEIW; AEIW DEC; 15.8g held behind 15.8f2; PLAN-INDEX row; GBMI raw pinned (no code)</name>
  <files>.planning/DECISIONS.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158AEIW-reply-2026-11-27.txt, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-asthma-eur-eaf-complement-check-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-insert-review-and-close-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/asthma_eur_gbmi_raw_sha256.tsv</files>
  <read_first>
    - 15.8f SUMMARY (gates, commits), $Q8/gate_158.sh (the Q-158AEIM block), $Q8/dec_15_8f.py (DEC script pattern)
    - DECISIONS.md entry DEC-2026-11-26-ta-r4-asthma-eur-eaf-disclose-no-filter
  </read_first>
  <action>
    1. `git rev-parse HEAD > $Q8/start_15_8f2.txt` (start check in <context>). Re-run every gate of 15.8f Task 1 step 1
       (`bash $Q8/gate_157j.sh`; `bash $Q8/gate_158.sh Q-158DIG Q-158R6S Q-158E7R Q-F3NL Q-158R7 Q-158R6G Q-158KW
       Q-158DFX Q-158AEI Q-158AEIM`; tracked-file checks on R6G (both files), KW, DFX, AEI, AEIM (added-in 456ae994);
       `bash $Q8/gate_158r2.sh`; `bash $Q8/gate_158a2.sh Q-158OR Q-158PAL Q-158EL`). Add a Q-158AEIW block to
       gate_158.sh as the Q-158AEIM block is written (`sed`-copied question after `Question Q-158AEIW (2026-11-27): `,
       S = c06539ae…ae2e, L = `Hold — do not insert`, F[] full file name, GATE_NC_* hooks); `bash $Q8/gate_158.sh
       Q-158AEIW` rc 0; `tail -n 1` assert; the two table sha256 values in its line 1 == `sha256sum` of
       aeiw_crosstab_15_8f.tsv and aeiw_rows_15_8f.tsv and == `$Q8/aeiw_tables_15_8f.sha256`. Three NCs
       (GATE_NC_MUTATE=1, GATE_NC_LABEL=`Approve as written`, one GATE_NC_SHA character) → exit 2 each; real gate rc 0
       after → `$Q8/gate_nc_15_8f2.txt`. All in `$Q8/gate_15_8f2.txt`. Any failure = STOP, nothing edited.
    2. `$Q8/dec_15_8f2.py` (from dec_15_8f.py; DECISIONS.md copied to `$Q8/DECISIONS.pre_15_8f2.md` first): append
       `## 2026-11-27 — DEC-2026-11-27-ta-r4-asthma-eur-eaf-sentence-held: the filled DRAFT (c) asthma EUR EAF sentence is
       not inserted; 15.8g waits on the complement check 15.8f2 and a newly approved sentence (Carter, Q-158AEIW)`.
       Bullets: Decider (Carter 2026-11-27, file, sha256, label, last line asserted, gate record and NCs); Measured
       (the lift_changed_ref counts of <context>, each with its denominator, read by the script from
       aeiw_crosstab_15_8f.tsv after its sha256 check); Relayed context (the orchestrator's 16 of 19 / 12 of 14 hand
       check and the 5:73331273 example, labelled as not in the reply file and not yet measured; measured by 15.8f2);
       Consequence (the 15.8f sentence, sha256 238768d4…e776, is withdrawn; any later (c) sentence is filled from
       15.8f2's manifests and approved in its own question); Not authorized (as the 15.8 entries: no fit, OSF, push or
       W4a-T3 lock; decision_rules.yaml locked: false; n_regions_min 7; no DRAFT edit; lifts nothing under D-28). Quote
       the reply with `cat` between ```text fences; extract it back and `cmp` with the reply file; the prefix
       `cmp -n` with the pre copy (else STOP).
    3. 15.8g (one script, old strings asserted unique): frontmatter `depends_on: ["ta-r4-W3f-15-8-review-suite-and-close"]`
       → `depends_on: ["ta-r4-W3f-15-8-review-suite-and-close", "ta-r4-W3f-asthma-eur-eaf-complement-check"]`; after the
       closing `---` of the frontmatter insert
       `<hold_note>` / `2026-11-27: Carter answered Q-158AEIW "Hold — do not insert"
       (DEC-2026-11-27-ta-r4-asthma-eur-eaf-sentence-held). This plan does not run as written. The 15.8f sentence
       ($Q8/aeiw_sentence_15_8f.txt) is withdrawn; a new (c) sentence must be filled from 15.8f2's manifests (and any
       correction Carter orders at Q-158EAFC) and re-approved by Carter in its own question, after which this plan is
       re-planned: its gate list adds Q-158AEIW and Q-158EAFC, its FULL base becomes full_15_8f2.xml and its SUMMARY
       set adds 15.8f2.` / `</hold_note>`; nothing else changes (`git diff --numstat` == 1 deletion + the note's
       lines, asserted). PLAN-INDEX: add the 15.8f2 row after 15.8f (`ta-r4-W3f-asthma-eur-eaf-complement-check-PLAN.md`,
       objective, `PLANNED`, gates Q-157J … Q-158AEIW; Q-158EAFC STOP); the 15.8g row's status text becomes `HELD
       (Q-158AEIW Hold); depends on 15.8f2 and a re-approved (c) sentence; re-plan before running`; the 15.8 paragraph
       gains `Amended 2026-11-27 (Carter Q-158AEIW Hold): order … → 15.8f → 15.8f2 → 15.8g; 15.8g re-planned after
       Q-158EAFC.` Commit `docs(ta-r4-W3f): Carter Q-158AEIW (Hold) reply + DEC; plan 15.8f2; 15.8g held behind it
       (15.8f2)`, explicit paths: DECISIONS.md, the AEIW reply, this PLAN, the 15.8g PLAN, PLAN-INDEX.
    4. Raw pin (sbatch, `-t 00:30:00 --mem=4G`): assert the raw file's header (<context>); draw a seeded sample of
       1,000 rows of the harmonized input across all chromosomes (`random.Random(20261127).sample` of its data-line
       numbers, counted in a first pass; the per-chromosome counts of the sample printed) and assert each has exactly
       one raw row with the same (CHR, POS, REF, ALT) and float(all_meta_AF) == float(EAF) (one streaming pass over the
       raw file; any miss = STOP: the file is not the input's source). Write manifests/asthma_eur_gbmi_raw_sha256.tsv in
       house format, one row `data/raw/region_analysis/sumstats/asthma.EUR.raw.gz`, size, sha256, source `GBMI 2021
       Asthma_Bothsex_eur_inv_var_meta_GBMI_052021_nbbkgt1.txt.gz per config/datasets.yaml gbmi_asthma, base_url
       https://gbmi-sumstats.s3.amazonaws.com; per config, not checksum-verified; seeded 1,000-row sample across all
       chromosomes equal to the harmonized GRCh38 input` (if an upstream checksum is recorded anywhere in config or the
       repo, compare it instead and drop the "not checksum-verified" label; its config md5 is "" today). Record in the
       LOG that raw files exist under data/raw/region_analysis/sumstats for bmi, hypertension and stroke EUR (listed with
       sizes; not read by this plan) and that none exists for t2d (its chain starts at its harmonized file).
       gate_reply.py free-text check of <question> (scratch reply in a tmp `--dir`; accept rc 0, mismatch rc 2) →
       `$Q8/gate_reply_freetext_15_8f2.txt`. test_storage_on_rs1.py::test_manifests_parse green. Commit
       `chore(ta-r4-W3f): GBMI asthma EUR raw file pinned (15.8f2)`, explicit path: the manifest.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash data/r4/tmp/w3f/q158/gate_157j.sh && bash data/r4/tmp/w3f/q158/gate_158.sh Q-158AEI Q-158AEIM Q-158AEIW && test "$(tail -n 1 .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158AEIW-reply-2026-11-27.txt)" = "Carter reply (verbatim, selected option): Hold — do not insert" && git ls-files --error-unmatch .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158AEIW-reply-2026-11-27.txt && grep -qF 'DEC-2026-11-27-ta-r4-asthma-eur-eaf-sentence-held' .planning/DECISIONS.md && head -8 .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-insert-review-and-close-PLAN.md | grep -qF 'depends_on: ["ta-r4-W3f-15-8-review-suite-and-close", "ta-r4-W3f-asthma-eur-eaf-complement-check"]' && test "$(head -1 .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/asthma_eur_gbmi_raw_sha256.tsv)" = "$(printf 'rel_path\tsize_bytes\tsha256\tsource')" && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_storage_on_rs1.py -q -p no:cacheprovider && git diff --quiet HEAD -- .planning/amendments/osf-amendment-r4-DRAFT.md</automated>
  </verify>
  <done>All gates pass, Q-158AEIW included, with its NCs failing; the AEIW DEC is committed with a cmp-equal quote; 15.8g depends on 15.8f2 and carries the hold note; PLAN-INDEX has the 15.8f2 row; the GBMI raw file is pinned; no src or test file changed.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: additive module functions; tests D and E (RED, then GREEN with NCs); measurement driver → per-row and cross-tab manifests; pilot exposure; findings and recommendation text (no DRAFT edit)</name>
  <files>src/python/ta_r4/orientation_eaf.py, tests/ta_r4/test_asthma_eur_eaf_complement.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_complement.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_complement_crosstab.tsv</files>
  <read_first>
    - src/python/ta_r4/orientation_eaf.py (all), tests/ta_r4/test_asthma_eur_eaf_disclosure.py (constants, sha256 and pin helpers)
    - data/r4/tmp/w3f/q158/multikey_15_8e.R, src/snakemake/scripts/ta_r4/variant_match.R (resolve_fit_names)
  </read_first>
  <behavior>
    - D and E RED before the functions exist (AttributeError / ImportError) and before the manifests exist; GREEN after
    - eaf_pattern(0.993201, 0.0151196734364025) == "complement"; eaf_pattern(0.4555, 0.241496001646436) == "other"; eaf_pattern(0.3003, 0.797690660177188) == "complement" at the defaults and "other" at agree_tol = complement_tol = 0.05; eaf_pattern(0.5, 0.605) == "other", and "agree" with agree_tol=0.11
    - verdict({"asthma": 0.99, "t2d": 0.015, "1kg": 0.02, "hypertension": None}) == "asthma_outlier"; verdict({"asthma": 0.99, "t2d": 0.015, "1kg": 0.98}) == "t2d_outlier"; verdict({"asthma": 0.99, "t2d": 0.015}) == "lt3_sources"
    - onekg_eaf("G", "GA", [(100, "GA", ["G"], ["0.02"])]) == ("swapped", approx 0.98); onekg_eaf("G", "A", [(100, "G", ["A", "T"], ["0.1", "0.2"])]) == ("exact", 0.1); onekg_eaf("A", "G", [(100, "G", ["A", "T"], ["0.1", "0.2"])]) == ("swapped", approx 0.7) (records = the 1000G lines at the row's POS)
    - left_aligned("CAT", "C", "true") == "true"; left_aligned("ATA", "A", "true") == "false"; left_aligned("AC", "GT", "true") == "undetermined"
  </behavior>
  <action>
    1. RED: write D and E per <new_tests>; run under sbatch (cascadelake, junit) → `$Q8/red_15_8f2.txt`.
    2. Module: append the new constants and functions of <interfaces> after the last 15.8f definition; change nothing
       above. `$Q8/additive_check_15_8f2.py` (ast of `git show $(cat $Q8/start_15_8f2.txt):src/python/ta_r4/orientation_eaf.py`
       vs HEAD; optional path argument for NCs): (a) `git diff --numstat <start> HEAD -- src` is exactly one line,
       0 deletions, path src/python/ta_r4/orientation_eaf.py; (b) every top-level def / assignment at start has an
       identical `ast.get_source_segment` at HEAD; (c) no new top-level name collides with a start name; (d) every new
       top-level statement is a FunctionDef or an Assign / AnnAssign to a new UPPER_CASE name; (e) no module-level
       Expr(Call) or other call statement anywhere at top level (docstring excepted). NC: a scratch copy with
       `def ref_match(ref, bases): return "true"` appended exits nonzero (`$Q8/additive_nc_15_8f2.txt`). Identity first: `render_eaf_manifest(eaf_diffs(".", TABIX))` sha256 ==
       7ad5ce50…80c0 (sbatch driver `$Q8/eaf_rebuild_15_8f2.py`; difference = STOP). Carve-out asserts as 15.8f (git
       grep pipeline empty; no tests import; test_storage_on_rs1.py green).
    3. Pilot exposure (sbatch, RSCRIPT absolute, `-t 01:00:00 --mem=16G`): the getParseData check and its two NCs
       first (`$Q8/eafc_pilot_parse_15_8f2.txt`; any failure = STOP), then `$Q8/eafc_pilot_15_8f2.R` per <context>,
       positive control first (it must report the planted member; else STOP), then the real run →
       `$Q8/eafc_pilot_members_15_8f2.tsv` (header asserted `fit_path\tmember_key`; sha256 in the LOG). Counts printed:
       fits read, fits with sets, sumstats_unpinned, members.
    4. Measurement driver `$Q8/eafc_15_8f2.py` (sbatch, cascadelake, `--mem=64G`, `-t 04:00:00` for this first run,
       which has no measured time yet; its elapsed time recorded): all_rows (one pass per
       window per file, 1000G read once per window) → grch38_rows for every indel and every per-row row (one lifted.bed
       pass) → input_fields (one pass) → raw_fields (one pass) → indel form, chain, exposure → both manifests via the
       render functions, rows in `_join` order. Then, before anything else is built on them, the STOP checks of
       must_haves truth 5: n(class ≠ palindromic_SNV and pattern_t2d ≠ unavailable) == 225 / 216,105 per group, equal to the
       aggregate manifest's (read); the 16 complement keys and 3
       other keys of <context> equal the rows the driver classifies, key by key (a count match with different keys is
       STOP); any chain row failing the lifted or oriented rule (<context>) is STOP. Reconcile: each cross-tab block
       sums to its denominator; the palindromic-row count equals an independent recount by `$Q8/eafc_palin_recount_15_8f2.py`
       (reads the oriented file and the catalog directly, not the module); the per-row manifest row count equals the
       cross-tab's count of rows with |ΔEAF| > 0.2 against at least one source. Any miss = STOP.
    5. Tests D and E green in one dedicated sbatch run (cascadelake; stdout `$Q8/green_de_15_8f2_<jobid>.out`, junit
       `$Q8/green_de_15_8f2_<jobid>.xml`, the only match of `green_de_15_8f2_*.xml`; `-t` = 2× the driver's measured
       elapsed time; D's runtime recorded and used to budget every later job). NCs
       (`$Q8/nc_15_8f2.txt`; each an in-place mutation of the file the test reads, sha256 before, restored by copy from
       `$Q8/nc_bak/`, sha256 equal after; PYTHONDONTWRITEBYTECODE=1; each NC job `-t` ≥ 2× D's green time, `--mem=64G`),
       cheap pin NC first: (i) one sha256 character in asthma_eur_gbmi_raw_sha256.tsv → D fails on the pin; (ii) one
       pattern_t2d value in the per-row manifest → D fails; (iii) one verdict value → D fails; (iv) one EAF_1kg value →
       D fails; (v) one raw_is_diff_AF_gnomAD value → D fails; (vi) one left_aligned_grch38 value → D fails; (vii) one
       cross-tab n and, separately, one denominator → D fails (two runs); (vii-b) one verdict_with_1kg value → D fails; (viii) `AGREE_TOL = 0.1` → `0.11` in the
       module → E fails (constant assert and the (0.5, 0.605) case; restored by sha256); (ix) the swapped multi-allelic rule `1 - sum(...)` → `1 - af[i]` in the
       module → E fails; (x) `open("nc_side_effect", "w").close()` appended to the module → E fails (tmp cwd not empty;
       the restore deletes nc_side_effect in the repo root and tmp cwd and asserts `test ! -e nc_side_effect`). Test A
       of 15.8f also run once after the module change (green; its byte identity covers the old functions). A test
       that does not fail on its NC = STOP.
    6. Findings and recommendation (script `$Q8/eafc_text_15_8f2.py`; numbers read from the committed-to-be manifests and
       `$Q8/eafc_pilot_members_15_8f2.tsv`, never typed) → `$Q8/eafc_findings_15_8f2.txt` and
       `$Q8/eafc_recommendation_15_8f2.txt` (one line each, templates and rule of <question>; the forbidden word list,
       causal words and "lead", asserted absent from the findings; the branch of the rule that fired and the three
       branch-2 conditions counted per file written to the LOG); the two manifests' sha256 → `$Q8/eafc_tables_15_8f2.sha256` (cross-tab,
       then per-row).
    7. Commit `feat(ta-r4-W3f): asthma EUR EAF complement check, diagnostic (orientation_eaf additive; patterns against
       four EUR files and 1000G EUR, source chain, indel form, exposure) (15.8f2)`, explicit paths: module, test file,
       the two manifests. Then `git diff --numstat $(cat $Q8/start_15_8f2.txt) HEAD -- src` is one line, 0 deletions,
       path src/python/ta_r4/orientation_eaf.py, and `$Q8/additive_check_15_8f2.py` passes (else STOP).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/additive_check_15_8f2.py && test "$(head -1 data/r4/tmp/w3f/q158/eafc_pilot_members_15_8f2.tsv)" = "$(printf 'fit_path\tmember_key')" && ! grep -qiw lead data/r4/tmp/w3f/q158/eafc_findings_15_8f2.txt && test "$(git diff --numstat $(cat data/r4/tmp/w3f/q158/start_15_8f2.txt) HEAD -- src | awk '{print $2, $3}')" = "0 src/python/ta_r4/orientation_eaf.py" && test "$(sha256sum < .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf.tsv | cut -d' ' -f1)" = 7ad5ce50abfb6255da90c7eec98d760308a96c2d1eac348d4b8194e6239080c0 && test -z "$(git grep -l orientation_eaf -- src workflow 'Snakefile*' config | grep -vx src/python/ta_r4/orientation_eaf.py)" && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import glob,xml.etree.ElementTree as E;f=glob.glob('data/r4/tmp/w3f/q158/green_de_15_8f2_*.xml');assert len(f)==1,f;N={'test_asthma_eur_eaf_complement_manifests_rederive','test_eaf_complement_rules_and_module_hygiene'};c=[t for t in E.parse(f[0]).iter('testcase') if t.get('name') in N];assert len(c)==2 and not [x for t in c for x in t if x.tag in ('failure','error','skipped')],c" && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_asthma_eur_eaf_complement.py tests/ta_r4/test_storage_on_rs1.py -q -p no:cacheprovider -k "not rederive" && test -s data/r4/tmp/w3f/q158/eafc_findings_15_8f2.txt && test -s data/r4/tmp/w3f/q158/eafc_recommendation_15_8f2.txt && git diff --quiet HEAD -- .planning/amendments/osf-amendment-r4-DRAFT.md</automated>
  </verify>
  <done>The module gained only new functions (old ones byte-identical by ast, aggregate manifest unchanged); the join reproduces 15.8f's denominators and the 16 complement keys one by one; both manifests are committed and rebuilt by D; D and E are green in their own sbatch run with every NC failing; pilot exposure is measured with a positive control; the findings and recommendation lines are on disk; the DRAFT is unchanged.</done>
</task>

<task type="auto">
  <name>Task 3: FULL under Slurm, reconciled; records (HANDOFF, STATE, LOG, PLAN-INDEX, SUMMARY); commit (no push)</name>
  <files>.planning/HANDOFF.json, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-asthma-eur-eaf-complement-check-SUMMARY.md (scratch: $Q8/full_15_8f2.xml, $Q8/check_15_8f2.py, $Q8/reconcile_15_8f2.txt)</files>
  <action>
    1. `$Q8/close.sh 15_8f2` under sbatch (`--constraint=cascadelake`, `--mem=96G`; 15.8f's FULL peaked at 66.9 GiB;
       `-t` = 2× (15.8f's FULL 2h26m + test D's measured runtime from the Task 2 green run)).
    2. `$Q8/check_15_8f2.py` (from check_15_8f.py, its 15.8c2 carve-out kept): (a) vs full_15_7j.xml with NEW = union of
       the `## New test ids` and declared = union of the `## Declared spec updates` of the ten 15.8a–f SUMMARYs (parsed;
       a missing section is STOP), plus this plan's 2 ids; expect = base totals read from full_15_7j.xml + Σ N_new
       (2,694 + 72 + 2 + 2 = 2,770). (b) vs full_15_8f.xml: removed 0, added == this plan's 2 ids (passed), every other
       id identical. Checker NC: full_15_8f.xml given as NEW fails. Arithmetic in `$Q8/reconcile_15_8f2.txt`. Any miss = STOP.
    3. HANDOFF (one script, data/r4/tmp/w3f/handoff_edit.py pattern): `W3f158f_Q158AEIW_pending` → `HELD 2026-11-27
       (Carter Q-158AEIW "Hold — do not insert", DEC-2026-11-27-ta-r4-asthma-eur-eaf-sentence-held); see 15.8f2`, old
       text kept under `W3f158f_Q158AEIW_pending_PRE_15_8f2`; add `W3f158f2_Q158EAFC_pending` (findings sha256, both
       table sha256, the recommendation branch; names-only pilot membership); `W3f158_asthma_eur_grch37_fasta` stays OPEN; `resume_on_reconnect` =
       await Carter Q-158EAFC (orchestrator writes the reply and its sha256), then the plan his answer names (15.8g is
       re-planned only after a (c) sentence is re-approved); `suite_baselines_ta_r4_latest` = full_15_8f2.xml counts.
       Key count after == before + added; every pre-existing string value still present.
    4. PLAN-INDEX 15.8f2 row `COMPLETE (ends at the Q-158EAFC STOP)` with commits, the headline counts (each with its
       denominator) and FULL. STATE ★ RESUME HERE — LATEST ★ (NEXT = Carter Q-158EAFC; 15.8g HELD; NOT PUSHED); prior
       block SUPERSEDED. LOG entry: gate records (AEIW added, NCs); DEC; the 15.8g diff; the raw pin and its seeded
       1,000-row check; the raw files present (bmi, hypertension, stroke EUR) and absent (t2d); reference provenance and
       the sources cited for the UK Biobank overlap (GBMI, Zhou et al. 2022; DIAMANTE 2022; Evangelou 2018; Yengo 2018),
       labelled cited, not measured;
       the gate_reply.py free-text check; the additive check and its NC; the identity checks and the 16-key check; the
       palindromic recount; pilot exposure (getParseData check and NCs, positive control, counts, members file sha256); the D/E green job id and
       runtime; NC results; the pattern rule, tolerances and verdict rule as used. SUMMARY with `## New test ids` (the 2
       ids, junit form) and `## Declared spec updates`: none.
    5. PINS (`pytest tests/m3/test_source_freeze_pins.py`); `git fsck --connectivity-only` before and after; commit
       `docs(ta-r4-W3f): 15.8f2 — asthma EUR EAF complement measurement, FULL reconciled, records; stops at Q-158EAFC
       (no push)`, explicit paths. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8f2.py && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import json,yaml;h=json.load(open('.planning/HANDOFF.json'));s=json.dumps(h);assert 'W3f158f2_Q158EAFC_pending' in s and 'W3f158f_Q158AEIW_pending_PRE_15_8f2' in s;d=yaml.safe_load(open('config/ta_r4/decision_rules.yaml'));assert d['locked'] is False;assert 'n_regions_min: 7' in open('config/ta_r4/decision_rules.yaml').read()" && test -z "$(git status --porcelain -- .planning/HANDOFF.json .planning/STATE.md .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-asthma-eur-eaf-complement-check-SUMMARY.md)" && git diff --quiet HEAD -- .planning/amendments/osf-amendment-r4-DRAFT.md</automated>
  </verify>
  <done>FULL 2,770 reconciled cumulatively and against 15.8f; records committed with explicit paths; HANDOFF points at Q-158EAFC; 15.8g held; the DRAFT is unchanged; nothing pushed.</done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 4: STOP — Q-158EAFC, Carter decides what follows the complement measurement</name>
  <files>(none written by the executor; the orchestrator writes W3f-carter-15-8-Q-158EAFC-reply-<date>.txt)</files>
  <what-built>Per-row and cross-tab manifests (sha256 in `$Q8/eafc_tables_15_8f2.sha256`), names-only pilot membership table, findings and recommendation lines. Q-158AEIW (Hold) recorded; 15.8g held behind 15.8f2.</what-built>
  <action>
    1. Return the checkpoint with Q-158EAFC in the two-line format of <question> (line 1 with the findings and
       recommendation copied from their files, not retyped, and the two table paths with their sha256), and for the
       orchestrator to show: the cross-tab blocks `pattern` (all references, by group × class), `verdict` (all three
       tolerances), `verdict_with_1kg`, `n_sources`, `reference_provenance`, `indel_form`, `chain` and the exposure tables; the per-row rows whose verdict is `asthma_outlier` or
       `t2d_outlier` (all columns); what `undetermined`, `lt3_sources` and `onekg_match == none` mean; that EAF cannot
       show which allele BETA refers to; that the four sumstats references are not independent (one harmonizer; and,
       per the published study descriptions (not measured here), the type 2 diabetes, hypertension and BMI files include
       UK Biobank, as does the GBMI asthma file); that a GRCh37 FASTA download (HANDOFF W3f158_asthma_eur_grch37_fasta) would
       decide the GRCh37-undetermined rows. Options in the <question> order, `Hold` first, none labelled Recommended.
    2. Stops even under --auto / yolo / --chain; the executor selects nothing, writes no reply file and edits nothing.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && test -z "$(ls .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158EAFC-reply-*.txt 2>/dev/null)" && git diff --quiet HEAD -- .planning/amendments/osf-amendment-r4-DRAFT.md</automated>
  </verify>
  <done>The question is presented; no reply file was written by the executor; 15.8f2 is complete. The orchestrator writes Carter's reply, states its sha256, and plans what it names.</done>
  <resume-signal>Orchestrator: Carter's reply file written and its sha256 stated. `Hold` → nothing follows until Carter re-decides; `Disclose only` → a new plan fills a (c) sentence from 15.8f2's manifests for a new approval question, then 15.8g is re-planned; `Treat as a data defect: plan a correction` → a new correction plan (not this one) before any sentence; `Other` → as Carter writes.</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| relayed hand check → record | the orchestrator's 16 / 19 count entered the brief unmeasured; only Task 2's key-by-key measurement may enter the question or a DEC as measured |
| external files → measurement | GBMI raw, 1000G VCFs, GRCh38 FASTA and four reference sumstats; each opened file pinned by sha256 and re-checked by test D |
| executor → Carter's decision | the recommendation could steer the answer; its rule is fixed in this plan before measurement and no option is labelled Recommended |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-158f2-01 | Tampering | reference and raw files | mitigate | house-format pins; test D re-checks size + sha256 of every file opened; NC (i) |
| T-r4-158f2-02 | Tampering | causal premise in the question | mitigate | symmetric verdict over ≥ 3 sources; verdict_with_1kg because the sumstats references share a harmonizer and UK Biobank; branch 2 needs 1000G agreement, variant-set membership and a non-repeat row; causal word list asserted absent; frequency-only wording; Carter decides |
| T-r4-158f2-03 | Tampering | 15.8f module behaviour | mitigate | additive-only ast check with NC; aggregate manifest sha256; test A re-run |
| T-r4-158f2-04 | Elevation | auto-mode answering EAFC | mitigate | first option `Hold`; executor never writes the reply; orchestrator states its sha256 |
| T-r4-158f2-05 | Information disclosure | pre-lock pilot results | mitigate | names only: colnames(fit$lbf_variable) and fit$sets$cs, enforced by getParseData symbols with NCs; output (fit_path, member_key) only; no fit, LD or purity run |
| T-r4-158f2-06 | Information disclosure | push / OSF | accept | none in 15.8 |
</threat_model>

<verification>
- Gates pass incl. Q-158AEIW with NCs; AEIW DEC committed with a cmp-equal quote; 15.8g depends on 15.8f2 with the hold
  note; the module change is additive and the aggregate manifest unchanged; the join reproduces n(non-palindromic, pattern_t2d ≠ unavailable) == 225 / 216,105 and the 16
  complement keys; both manifests rebuilt by D; D and E green with every NC failing; FULL 2,770 reconciled; records
  committed; Q-158EAFC presented with `Hold` first; DRAFT unchanged; decision_rules.yaml locked false; n_regions_min 7;
  nothing pushed.
</verification>

<success_criteria>
- Carter can see, with every count beside its denominator, whether the asthma EUR file, the t2d EUR file or neither is
  the source attaching frequencies to the opposite allele, at which stage, for which indel forms, and whether any such
  row touches a production fit key or a pilot credible set, before any sentence or correction is written.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-asthma-eur-eaf-complement-check-SUMMARY.md`
</output>
