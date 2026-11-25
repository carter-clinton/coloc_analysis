---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8e
slug: W3f-multikey-fatal-and-chronology
type: execute
wave: 15.8e
depends_on: ["ta-r4-W3f-e7-filtered-cs-counts"]
gap_closure: true
files_modified:
  - src/snakemake/scripts/ta_r4/cs_cross_purity.R
  - tests/ta_r4/test_cs_cross_purity_resolution.py   # test_multi_key_base_is_refused_and_counted_in_production_… (declared) + 1 new test
  - tests/ta_r4/test_amendment_text.py                # 1 new test (Purpose chronology)
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-multikey-fatal-and-chronology-SUMMARY.md
autonomous: false
requirements:
  - REQ-OSF-PREREG

must_haves:
  truths:
    - "Gates Q-157J and Q-158R7 (`Approve as written (Recommended)`, sha256 a9a6866e…61b8) pass (15.8 protocol); otherwise nothing is edited"
    - "Measured before the change, with variant_match.R resolve_fit_names only (no cross-panel purity is computed on any pilot fit, so no new pre-lock inspection of results): over every credible-set member name of the 20 production-panel pilot fits (A3_1kg_newcat), resolved through the r4 sumstats, r4 catalog and EUR_1kg_r4 fit panel as cs_cross_purity.R would, the number whose base has more than one allele key; and the catalog-level bound, the number of rsids with more than one normalized allele key in each of the 31 r4 catalogs (plan-checker 2026-11-25: 0), recorded as holding for the current catalogs only. A non-zero member count is a STOP for Carter (production aggregation would now stop with an error)"
    - "cs_cross_purity.R stops with `REFUSED_MULTI_KEY: <n> of <m> credible-set members of <fit> (first: …)` when any member resolves to more than one allele key without --allow-duplicate-rows, with or without --allow-absent; --allow-duplicate-rows behaviour (the (N+1)-th key in catalog order; BAD_OCCURRENCE) is unchanged; the output columns are unchanged (n_refused_multi_key stays and is 0 in every written row)"
    - "DRAFT (e) E4: `A member whose name resolves to more than one allele key is left out of the purity and counted, and its set is noted.` → `A member whose name resolves to more than one allele key is an error.`"
    - "DRAFT Purpose keeps `before any production-arm fit exists` and gains the R7 sentence Carter approved (Q-158R7) exactly: the inserted text, unwrapped, has sha256 59c2631a6baa441c44754bbf3d55cb1f0eadd7b18356b7af6762d92a557672be (416 characters), asserted before and after insertion; (h) and the approved pilot-fit paragraph are untouched (test_draft_paragraph_equals_the_approved_file_unwrapped green)"
  artifacts:
    - path: "src/snakemake/scripts/ta_r4/cs_cross_purity.R"
      provides: "multi-key member is fatal"
  key_links:
    - from: "cs_cross_purity.R fatal-status loop"
      to: "variant_match.R resolve_fit_names status refused_multi_key (:124)"
      via: "status code list"
      pattern: "refused_multi_key"
---

<objective>
Close R5 and R7 as Carter chose ("R5 and R7: go with recommendation"). R5: a cross-panel purity member that resolves to
more than one allele key is silently left out (cs_cross_purity.R:58-62, :87-90), which contradicts the strict
complete-membership rule elsewhere; it becomes an error. R7: the Purpose's "before any production-arm fit exists" is
restated as gated production execution vs pilot fitting.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-157J: as in ta-r4-W3f-collector-drop-audit-PLAN.md <question>.
Q-158R7 (answered 2026-11-25): file `W3f-carter-15-8-Q-158R7-reply-2026-11-25.txt`, sha256
`a9a6866eb9c4b518c7a98206273ddd55fe0cbd4e2e49c1b3d7264d2f69a261b8`, label `Approve as written (Recommended)`: the R7
sentence in <context> exactly as written (question text in 15.8a's <question> table).
Task 1 STOP question (only if the measured count is non-zero), QID Q-158R5, file `W3f-carter-15-8-Q-158R5-reply-<date>.txt`:
"N credible-set members of the production-panel pilot fits resolve to more than one allele key; with the R5 change the
production cross-purity step would stop with an error on these fits. How should 15.8e proceed?" Labels: `A: Make it
fatal anyway; production must resolve these first (new plan)` / `B: Keep the exclusion, disclosed with the measured
count (DRAFT only)` / `C: Other (free text)`. No Recommended label until the members are inspected; the executor states
its recommendation with the list.
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-collector-drop-audit-PLAN.md
@src/snakemake/scripts/ta_r4/cs_cross_purity.R
@src/snakemake/scripts/ta_r4/variant_match.R
@tests/ta_r4/test_cs_cross_purity_resolution.py

**Verified at planning (99ab219d).**
- variant_match.R :124 `if (!isTRUE(allow_duplicate_rows)) return(row("refused_multi_key"))` for a base with k > 1 keys.
- cs_cross_purity.R :58-62 fatal loop over `c("duplicate_row", "bad_occurrence", "unresolved")`; :86-90 refused members
  are skipped before the UNMATCHED check; :100-101 note `refused_multi_key`; :111 `n_refused_multi_key`. The header
  comment (:7-8) describes the refusal.
- tests.ta_r4.test_cs_cross_purity_resolution::test_multi_key_base_is_refused_and_counted_in_production_and_chosen_by_catalog_order_only_when_allowed
  (:401-419) asserts the production path returns 0 with the member counted → declared spec update: its production
  block asserts a non-zero exit with `REFUSED_MULTI_KEY` and `rsM` in stderr; the --allow-duplicate-rows and
  BAD_OCCURRENCE blocks are unchanged. The id stays (protocol), though its name says "counted".
- Plan-checker (2026-11-25): 0 rsids with more than one allele key across the 31 r4 catalogs.
- 15.7c measured 0 multi-key bases over 33,438 names of the pre-15.5a fits (`data/r4/tmp/w3f/q157/c157/f10_real_fit_routes_rerun.tsv`);
  the production-panel pilot fits on the current catalogs have not been measured.
- run_aggregation.CROSS_PURITY (:51-53): the only pair with A3_1kg as fit arm is ("A3_1kg", "A3_ukb", True).
- Purpose (DRAFT line 83 at planning): `**Purpose:** to fix, before any production-arm fit exists (the pre-lock pilot
  fits are listed in (h)), the arms, …`; the required phrase is checked by
  tests/ta_r4/test_prelock_pilot_fits.py:79 (not by test_amendment_text.py).

**R7 wording (Carter approved it as written, Q-158R7; inserted byte-for-byte, its hard line wraps joined with single
spaces; sha256 of the joined text 59c2631a…72be; no rewording, a length or framing failure is STOP).** Remove ` (the pre-lock pilot fits are listed
in (h))` from the Purpose sentence and add after that sentence: `Production-arm fits run only after the lock, through
the lock gate described in the status paragraph above. The pilot fits listed in (h) ran before the lock, outside that gate, on the corrected inputs
and partly on the production EUR panel, and were inspected; the lock therefore separates gated production execution
from pilot fitting, and does not mean that no fitted result was seen before the analysis was fixed.`
</context>

<new_tests>
N_new = 2.
1. tests/ta_r4/test_cs_cross_purity_resolution.py::`test_multi_key_member_is_fatal_with_or_without_allow_absent`
2. tests/ta_r4/test_amendment_text.py::`test_purpose_states_gated_production_vs_pilot_fitting` (the phrase, the gate
   sentence and the pilot sentence present in the extract; the old parenthetical absent)
Expected FULL: base full_15_8d.xml (expected 2,732) + 2 = 2,734. Declared: test_multi_key_base_is_refused_and_counted_in_production_and_chosen_by_catalog_order_only_when_allowed.
</new_tests>

<tasks>

<task type="auto">
  <name>Task 1: Gate; measure multi-key members on the production-panel pilot fits (STOP if non-zero)</name>
  <files>(scratch only: $Q8/multikey_15_8e.tsv)</files>
  <read_first>
    - cs_cross_purity.R (all); variant_match.R :60-140; run_aggregation.py :115-160 (runner argv)
    - manifests/prelock_pilot_fits.tsv (the A3_1kg_newcat rows)
  </read_first>
  <action>
    0. `git rev-parse HEAD > $Q8/start_15_8e.txt`; `bash $Q8/gate_157j.sh`; `bash $Q8/gate_158.sh Q-158R7`.
    1. For each A3_1kg_newcat pilot fit with sets: read only the fit RDS's member names (`colnames(fit$lbf_variable)`
       at `unlist(fit$sets$cs)`; no LD, no purity, no colocalization), and call `resolve_fit_names` (sourced from
       variant_match.R) with the r4 sumstats window, the r4 catalog and the EUR_1kg_r4 fit panel's variants, without
       --allow-duplicate-rows. Do not run cs_cross_purity.R on any pilot fit. Slurm `-t 00:30:00 --mem=16G`. Write
       `$Q8/multikey_15_8e.tsv` (fit, n_members, n_refused_multi_key, names). A missing input is recorded, not guessed.
       Also the catalog-level bound: for each of the 31 r4 catalogs, rsids with more than one normalized allele key
       (catalog_unique_key.py's key) → `$Q8/multikey_catalogs_15_8e.tsv` (expected 0 everywhere, per the plan-checker;
       recorded in the SUMMARY as holding for the current catalogs only — a catalog rebuild, e.g. under 15.8a Q-158R2 B,
       requires re-measuring). A non-zero catalog count with a zero member count is recorded, not a STOP.
    2. Total 0 → continue. Non-zero → STOP: present Q-158R5 with the list (checkpoint:human-action semantics, stops
       even under --auto); no edit until Carter's reply file exists and its sha256 is pinned here.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash data/r4/tmp/w3f/q158/gate_157j.sh && bash data/r4/tmp/w3f/q158/gate_158.sh Q-158R7 && test -s data/r4/tmp/w3f/q158/multikey_15_8e.tsv</automated>
  </verify>
  <done>The multi-key exposure of the production-panel fits is measured (0, or Carter has decided).</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: REFUSED_MULTI_KEY is fatal (RED first); DRAFT E4 + Purpose</name>
  <files>src/snakemake/scripts/ta_r4/cs_cross_purity.R, tests/ta_r4/test_cs_cross_purity_resolution.py, tests/ta_r4/test_amendment_text.py, .planning/amendments/osf-amendment-r4-DRAFT.md</files>
  <behavior>
    - Test 1: the rsM fixture of the existing multi-key test, production mode, with and without --allow-absent → exit ≠ 0, `REFUSED_MULTI_KEY` and `rsM` in stderr, no output file
    - Test 2: per <new_tests>
  </behavior>
  <action>
    1. RED: tests 1-2 and the declared edit of the existing multi-key test → fail (`$Q8/red_15_8e.txt`).
    2. cs_cross_purity.R: add `"refused_multi_key"` to the fatal status vector at :58 (message code
       `REFUSED_MULTI_KEY` via `toupper`); update the header comment's description of the refusal (:7-8) to say it is
       an error unless --allow-duplicate-rows. No other line changes (the per-set counting stays and writes 0).
    3. DRAFT script (one script, each old string asserted unique): the E4 sentence and the Purpose change in <context>;
       the script takes the R7 sentence from this plan's <context>, joins the wraps, asserts its sha256 equals the pinned
       value, inserts it, and asserts the DRAFT now contains it exactly once.
    4. Green: tests 1-2, test_cs_cross_purity_resolution.py, test_cs_cross_purity.py, test_reporting_widened.py,
       test_run_aggregation.py, test_amendment_text.py, test_prelock_pilot_fits.py.
    5. NCs (`$Q8/nc_15_8e.txt`): remove "refused_multi_key" from the vector → test 1 fails; restore the old
       parenthetical in the DRAFT → test 2 fails; md5/sha256-restore each. Commit (`fix(ta-r4-W3f): cross-panel purity
       member with several allele keys is an error (R5); Purpose chronology as gated production vs pilot fitting (R7) (15.8e)`).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_cs_cross_purity_resolution.py tests/ta_r4/test_cs_cross_purity.py tests/ta_r4/test_reporting_widened.py tests/ta_r4/test_amendment_text.py tests/ta_r4/test_prelock_pilot_fits.py -q -p no:cacheprovider</automated>
  </verify>
  <done>A multi-key member stops cross-panel purity; DRAFT E4 and Purpose describe the code and the chronology.</done>
</task>

<task type="auto">
  <name>Task 3: FULL vs full_15_8d.xml; records (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-multikey-fatal-and-chronology-SUMMARY.md</files>
  <action>
    `$Q8/close.sh 15_8e`; `$Q8/check_15_8e.py` (base full_15_8d.xml; NEW = 2; declared = the multi-key test id).
    Records: LOG (gate, measurement, NCs, check), PLAN-INDEX 15.8e row, STATE (NEXT = 15.8f; NOT PUSHED), SUMMARY with
    both sections. fsck; commit explicit paths. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8e.py</automated>
  </verify>
  <done>R5 and R7 closed; FULL reconciled; not pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| fit member names → cross-panel purity | an ambiguous member must not change purity silently |
| public chronology claim | must not imply no fitted result was seen before the lock |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-158e-01 | Tampering | silent member exclusion | mitigate | REFUSED_MULTI_KEY fatal; production-panel exposure measured first |
| T-r4-158e-02 | Repudiation | chronology overstated | mitigate | Purpose states gated execution vs pilot fitting; test 2 |
</threat_model>

<verification>
- check_15_8e.py passes; multikey measurement recorded.
</verification>

<success_criteria>
- Cross-panel purity has no silent exception; the Purpose claims only what the gate enforces.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-multikey-fatal-and-chronology-SUMMARY.md`
</output>
