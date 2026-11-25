---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8a4
slug: W3f-sumstats-orientation-eligibility-and-draft
type: execute
wave: 15.8a4
depends_on: ["ta-r4-W3f-sumstats-orientation-consumers"]
gap_closure: true
files_modified:
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158EL-reply-<date>.txt   # committed as received
  - .planning/DECISIONS.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv   # re-pinned from the re-measurement (identities in Task 1)
  - tests/ta_r4/test_sumstats_orient_draft.py
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-eligibility-and-draft-SUMMARY.md
autonomous: false
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Gates Q-157J, Q-158R2, Q-158OR, Q-158PAL and Q-158EL (gate_158a2.sh extended with Q-158EL's text, label and pinned sha256) pass; otherwise nothing is edited"
    - "The N1 eligibility measurement (measure_fit_eligibility plan/run/summarise, cap 0, no fit) is re-run on the oriented inputs: the run list equals the pinned manifest's measured keys (83); every row key of the new table equals the pinned table's (815)"
    - "Identities, each a STOP on failure: (a) bound rows differ from the pinned table only in sumstats_sha256 (the bound is the panel size, independent of the sumstats); (b) for bmi EUR and t2d EUR (0 flips) every measured n_variants_pre_ld and n_variants equals the pinned value; (c) every measured n_variants_pre_ld equals after_exact + after_both of manifests/sumstats_r4_orientation.tsv for that trait × region (the R fit join and the Python classification agree); (d) n_variants never falls for any measured row; (e) for every measured row, n_variants(new) − n_variants(pinned) ≤ n_variants_pre_ld(new) − n_variants_pre_ld(pinned) (panel restriction cannot add more rows than the catalog join added), so every row not in the Q-158EL set is shown under the cap by its own measured count and this bound, not only by the set check"
    - "The fits whose eligibility changes are exactly the set Carter was shown in Q-158EL; a different set is a STOP with a new question (Q-158EL2), not a re-pin"
    - "w3f_fit_eligibility.tsv is re-pinned from the summarised table only after (a)-(e) and the Q-158EL set check pass"
    - "DRAFT: (c)'s inputs parenthetical says the source sha256 are recorded and the oriented copies are verified in every production job; (c) lists the oriented input sha256 and states the orientation step with per-trait counts from the manifest, the fixed-point result (31 of 31 catalogs unchanged) and the A/T, C/G rule (dropped from fits; kept by the all-variant A1); (c)'s collection clause states the 15.8a audit counts (the clause 15.8a deferred); (i) names the orientation step; the measured-counts row states the oriented-input eligibility; every number is read from a manifest by the DRAFT script and re-derived by a test; old strings asserted unique; test_amendment_text.py and test_prelock_pilot_fits.py green (a framing or length failure is STOP)"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv"
      provides: "N1 eligibility on the oriented inputs"
    - path: "tests/ta_r4/test_sumstats_orient_draft.py"
      provides: "DRAFT numbers == manifests"
  key_links:
    - from: "w3f_fit_eligibility.tsv n_variants_pre_ld"
      to: "sumstats_r4_orientation.tsv after_exact + after_both"
      via: "identity (c)"
      pattern: "after_exact"
---

<objective>
Finish Carter's Q-158R2 D. Re-measure the post-restriction variant counts (review N1) on the oriented inputs, since
up to a third more rows now reach some fits and the 16,000 cap applies after panel restriction; re-pin the
eligibility table only behind identities; and state the orientation step, its counts and the collector audit in the
DRAFT. Closes review R2 (the clause 15.8a deferred under Carter's D).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-157J, Q-158R2, Q-158OR, Q-158PAL: as in ta-r4-W3f-sumstats-orientation-harmonize-PLAN.md <question>.

Q-158EL, asked by the orchestrator before 15.8a2 executes (answered once; this plan gates it), verbatim:
`Q-158EL (15.8a4, the 16,000-variant cap). With the oriented inputs more rows reach the fits, and the pre-registered cap (16,000 variants after panel restriction; above it the fit is not run and its pair rows are method none) is re-measured. My estimate from the panels (not a fit; it reproduces the current pinned counts exactly): type 2 diabetes AFR x BMI_5q13_3 goes over the cap in AFR661_A3 (14,398 to about 16,966 variants), AFR661_A2 (the same variants) and AFR504_A3 (14,343 to about 16,841), so those 3 fits would not run and in each AFR arm the stroke x type 2 diabetes row of BMI_5q13_3 becomes method none (4 to 5 of 30 rows per arm); type 2 diabetes AFR x PYHIN1_1q23 rises to about 15,832 and 15,718, just under. All other measured fits stay under the cap; every EUR fit's eligibility is unchanged. If the re-measurement shows exactly this set, should the cap apply as pre-registered, with the counts updated in the DRAFT? A different set stops for you again.`
Labels: `A: Apply the cap as pre-registered and update the counts (Recommended)` / `B: Stop before any re-pin and decide after seeing the measured counts` / `C: Other (free text)`.
Gate text: as in ta-r4-W3f-sumstats-orientation-harmonize-PLAN.md <question> (the saved line 1 omits the leading
`Q-158EL `; gate with the text minus it).
File `W3f-carter-15-8-Q-158EL-reply-2026-11-25.txt`, sha256 `f4ecd06606a6f9eb828b57a304da1663078e888494853818ba124ea3618b409c`. Label A → Task 1 proceeds when
the measured set equals the estimate set; label B → Task 1 measures, writes nothing to the manifest, and stops with
the measured table (QID Q-158EL2, same labels without "estimate"). A measured set different from the estimate set →
Q-158EL2 either way.
</question>

<protocol>
The 15.8 shared protocol (ta-r4-W3f-collector-drop-audit-PLAN.md) with the 15.8a2 sub-chain changes. Base
`$Q8/full_15_8a3.xml` (expected 2,722; use its actual totals). Scratch `$Q8/a4/`; measurement out-dir
`data/r4/tmp/elig_15_8a4` (measurement_argv refuses anything outside data/r4/tmp).
</protocol>

<context>
@src/python/ta_r4/measure_fit_eligibility.py
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation.tsv
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalog_collector_drops.tsv
@.planning/amendments/osf-amendment-r4-DRAFT.md

**Premise (planning, 8da7bfbe).** w3f_fit_eligibility.tsv: 815 rows = 83 measured (Slurm 1968979 / 1987407) + 732
bound (panel n_var ≤ 16,000, so the fit cannot exceed the cap whatever the sumstats); 10 measured rows ineligible
(A3_ukb asthma × BMI_5q13_3, PYHIN1_1q23; AFR661_A3 / AFR661_A2 / AFR504_A3 asthma × the same two). 57 measured rows
are of traits whose inputs change (hypertension, stroke, t2d AFR, asthma). Planner estimate (`data/r4/tmp/w3f/q158/planner_15_8a2/postld.R` → `postld2.tsv`, Slurm 2093481: catalog join + the fit's
panel 4-key rule in R on the real panels; reproduces n_variants_pre_ld and n_variants of the pinned table exactly for the 6 keys
checked): t2d AFR × BMI_5q13_3 AFR661_A3 14,398 → 16,966, AFR504_A3 14,343 → 16,841 (AFR661_A2 = AFR661_A3's variant
frame); t2d AFR × PYHIN1_1q23 13,341 → 15,832 and 13,265 → 15,718; A3_ukb asthma × SLC2A9_urate 14,263 → 14,402;
A3_ukb hypertension × PYHIN1_1q23 6,414 → 9,154. Estimate set for Q-158EL = {AFR661_A3, AFR661_A2, AFR504_A3} × t2d AFR ×
BMI_5q13_3 (eligible true → false). Pre-LD rows (planner, `data/r4/tmp/w3f/q158/planner_15_8a2/orient2.tsv`): t2d AFR
× BMI_5q13_3 23,718 → 28,840 and × PYHIN1_1q23 22,260 → 27,281; hypertension and stroke EUR stay below 8,000 in every
panel region. The DRAFT measured-counts row (table line "Measured post-restriction counts …") and (c) are the texts
to change; (c) still has the clause `the collection step before it keeps one row per rsid and omits unnamed variants
at a position that carries an rsid, without an audit` (15.8a did not edit it under D).
</context>

<new_tests>
tests/ta_r4/test_sumstats_orient_draft.py; N_new = 6 (no parametrize).
1. `test_eligibility_on_oriented_inputs_reconciles` (identities (a)-(e) recomputed from the two manifests and a typed
   copy of the pre-15.8a4 table at `$Q8/a4/w3f_fit_eligibility.pre.tsv`, whose sha256 is typed in the test)
2. `test_eligibility_manifest_records_the_oriented_sumstats` (every row's sumstats_sha256 == the oriented pin of its trait)
3. `test_draft_orientation_sentence_matches_the_manifests` (per-trait flip counts, the total, the A/T-C/G count and
   "31 of 31" from sumstats_r4_orientation.tsv and catalogs_r4_fixed_point.tsv)
4. `test_draft_collection_clause_matches_the_collector_audit` (722,928 / 31 / 162,724 / 159,969 / 2,755 re-derived
   from catalog_collector_drops.tsv)
5. `test_draft_inputs_list_the_oriented_sha256` (each of the 8 oriented sha256 appears once in (c) and equals the pin; the
   old inputs parenthetical ("verified inside every production fit … for the summary statistics") is absent and the new one present)
6. `test_draft_eligibility_counts_match_the_manifest` (the oriented-input counts above 16,000 per arm, re-derived)
Expected FULL: base full_15_8a3.xml (expected 2,722) + 6 = 2,728; declared none.
</new_tests>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Gates; eligibility re-measurement on the oriented inputs; identities; re-pin (or STOP)</name>
  <files>.planning/DECISIONS.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv, tests/ta_r4/test_sumstats_orient_draft.py</files>
  <behavior>
    - Tests 1-2 per <new_tests> (RED: the pinned table records the source sha256)
  </behavior>
  <action>
    0. `mkdir -p $Q8/a4`; HEAD → start.txt; gates (gate_157j.sh, gate_158r2.sh, gate_158a2.sh Q-158OR Q-158PAL
       Q-158EL after adding Q-158EL's Q/S/L entry to gate_158a2.sh; its NC: one changed byte → exit 2). Confirm 15.8a3
       closed. Commit 1: the Q-158EL reply as received + its DEC bullet appended under
       DEC-2026-11-25-ta-r4-sumstats-orientation (`cat` + `cmp`).
    1. `cp` the pinned table to `$Q8/a4/w3f_fit_eligibility.pre.tsv`; sha256 into `$Q8/a4/sha_before.txt`. RED tests 1-2.
    2. `measure_fit_eligibility plan --out-dir data/r4/tmp/elig_15_8a4 --rscript <r_coloc Rscript>`; assert the run list
       keys == the 83 measured keys of the pre table (else STOP). Submit its run.sh array under sbatch (as 15.5 did,
       `--constraint=cascadelake`); every task COMPLETED; `summarise --tsv $Q8/a4/w3f_fit_eligibility.new.tsv`.
    3. Identities (a)-(e) of must_haves into `$Q8/a4/identities.txt`; any failure STOP (record, no re-pin). Eligibility
       change set (rows whose `eligible` differs) vs the Q-158EL estimate set: equal and label A → step 4; otherwise
       print the measured table, ask Q-158EL2 as a `checkpoint:human-action` (stops under --auto; only Carter's typed
       reply creates the file) and stop.
    4. Re-pin: copy the new table over manifests/w3f_fit_eligibility.tsv; `diff` against the pre table shows only
       sumstats_sha256 on bound rows and the measured rows' counts/flags; tests 1-2 green. NC (`$Q8/nc_15_8a4.txt`): one
       measured n_variants_pre_ld changed by 1 in a temp copy → test 1 fails; md5-restore.
    5. Commit 2 (`test(ta-r4-W3f): N1 eligibility re-measured on the oriented inputs, identities (15.8a4)`).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash data/r4/tmp/w3f/q158/gate_158a2.sh Q-158OR Q-158PAL Q-158EL && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_sumstats_orient_draft.py -q -p no:cacheprovider -k "eligibility"</automated>
  </verify>
  <done>Eligibility on the oriented inputs measured, reconciled by four identities, and re-pinned (or Carter has the table).</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: DRAFT (c), (i) and the measured-counts row (RED first)</name>
  <files>.planning/amendments/osf-amendment-r4-DRAFT.md, tests/ta_r4/test_sumstats_orient_draft.py</files>
  <behavior>
    - Tests 3-6 per <new_tests>, RED against the pre-edit DRAFT
  </behavior>
  <action>
    1. RED tests 3-6 → `$Q8/red_15_8a4.txt`.
    2. `$Q8/a4/draft_15_8a4.py` (one script; every number read from the manifests; each old string asserted unique):
       (a0) (c): replace the parenthetical `Inputs (sha256 recorded before production and verified inside every
       production fit, colocalization and QTL job for the summary statistics, variant catalogs and harmonized QTL files
       it reads; a mismatch or an unlisted input fails the job):` (unique at planning) with `Inputs (sha256 recorded
       before production; production jobs read the oriented copies of these summary statistics listed below, and every
       production fit, colocalization and QTL job verifies the sha256 of those copies, the variant catalogs and the
       harmonized QTL files it reads; a mismatch or an unlisted input fails the job):`. After 15.8a3 the jobs verify the
       oriented sha256, not the source ones, so the source list is "recorded" only.
       (a) (c): after the inputs list ending `…(Suzuki 2024, effective N), \`23347618…\`.`, insert: `Production jobs read,
       and verify by sha256 in every production job, copies of these files written in the variant catalog's allele
       orientation (below): <trait ancestry `sha`; ×8>.` (b) (c): replace the collection clause quoted in <context> with: `the collection
       step before it keeps one row per rsid, omits an unnamed variant at a position that carries an rsid or a second
       unnamed variant at the same position, and every row it omits is listed, with the reason, in an audit file made by
       replaying that step on the same inputs (<N_drop> rows over <n_regions> regions; <N_lost> of them with an allele
       key that is not in the catalog: <N_swapped> the same variant written the other way round, which the orientation
       step restores, and <N_absent> with an allele pair the catalog does not hold, which are not fitted)`. (c) (c):
       after the sentence ending `…stops with an error.`, insert: `The catalog keeps each variant in the allele
       orientation of the first file that names it and the fits join it on chromosome, position, REF and ALT exactly,
       so before fitting each summary-statistics file is put in that orientation: where the catalog holds a row's
       variant only with REF and ALT exchanged, the row's REF and ALT are exchanged, BETA negated and EAF replaced by
       1 − EAF (<N_flip> rows in the <n_regions> regions: <per-trait counts, trait order of the inputs list>; A/T and
       C/G SNPs, <N_pal> of them, are treated the same way and are dropped from the fits by the allele-aware panel join;
       the all-variant A1 analysis, which matches alleles as an unordered pair and does not depend on the sign, keeps
       them),
       after which no row matches the catalog only the other way round; rebuilt from these files, <n_fp> of
       <n_regions> catalogs are byte-identical, so no catalog or panel changed.` (d) (i): after `In R4, EUR panels carry
       REF/ALT,` insert `summary statistics are first put in the variant catalog's orientation ((c)),`. (e) the
       measured-counts row: append `On the oriented inputs (15.8a4; Slurm <job>, <n>/<n> COMPLETED): above 16,000:
       <per arm counts>; total <N>; pre-LD rows equal the orientation manifest in <m>/<m> measured fits.`
    3. Tests 3-6, test_amendment_text.py, test_prelock_pilot_fits.py green (framing/length failure = STOP, no
       rewording to pass). Commit 3.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_sumstats_orient_draft.py tests/ta_r4/test_amendment_text.py tests/ta_r4/test_prelock_pilot_fits.py -q -p no:cacheprovider</automated>
  </verify>
  <done>The DRAFT states the orientation step, the audit and the oriented-input eligibility, each number re-derived by a test.</done>
</task>

<task type="auto">
  <name>Task 3: FULL vs full_15_8a3.xml; records (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-eligibility-and-draft-SUMMARY.md</files>
  <action>
    1. `$Q8/close.sh 15_8a4` under sbatch; `$Q8/check_15_8a4.py`: base full_15_8a3.xml, NEW = 6, declared none,
       expect = base totals + 6.
    2. Records: LOG (gate output, run list, identities, eligibility diff, DRAFT old/new strings, check output); R2
       recorded as resolved by 15.8a2-a4 (for 15.8f's review row); PLAN-INDEX 15.8a4 COMPLETE; STATE ★ (NEXT = 15.8b;
       NOT PUSHED); SUMMARY with `## Declared spec updates` (none) and `## New test ids` (6). fsck; commit explicit
       paths. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8a4.py && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import yaml;d=yaml.safe_load(open('config/ta_r4/decision_rules.yaml'));assert d['locked'] is False and d['confirmatory']['n_regions_min']==7"</automated>
  </verify>
  <done>FULL reconciled; records committed; not pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| measurement → public DRAFT numbers | every number must come from a manifest that a test re-derives |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-158a4-01 | Tampering | eligibility re-pinned without proof | mitigate | identities (a)-(e); change set == the set Carter saw, else STOP |
| T-r4-158a4-02 | Repudiation | DRAFT numbers typed by hand | mitigate | DRAFT script reads manifests; tests 3-6 re-derive |
| T-r4-158a4-03 | Tampering | silent change to a pre-registered rule | accept | the cap rule is unchanged; only its measured consequence moves, shown to Carter (Q-158EL) |
</threat_model>

<verification>
- Gates pass; identities hold; check_15_8a4.py passes; DRAFT tests green.
</verification>

<success_criteria>
- The eligibility record and the DRAFT describe the fits that production will run on the oriented inputs; R2 closed.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-eligibility-and-draft-SUMMARY.md`
</output>
