---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 12
slug: W3b-sh2b3-known-answer-and-findings
type: execute
wave: 12
depends_on: ["ta-r4-W3a-known-answer-routes"]
files_modified:
  - src/snakemake/rules/ta_r4_repro.smk
  - src/snakemake/rules/ta_r4_finemap.smk
  - src/python/ta_r4/commands.py
  - src/python/ta_r4/sh2b3_known_answer.py
  - tests/ta_r4/test_sh2b3_known_answer.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/known_answer_sh2b3.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_repro_sh2b3_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/legacy_code_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/W3b-T3.yaml
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: false
requirements:
  - REQ-SUSIE-RSS-POLICY
  - REQ-OSF-PREREG

must_haves:
  truths:
    - "The SH2B3 R2 known answer is reproduced in its EXACT configuration: L=15 fits at the R2 policy (config/susie_policy_L15.yaml; max_iter values recorded) for bmi/hypertension/stroke EUR on the legacy-identical panel, with the code at the R2-fire commit, plus the Stage-2 L=10 asthma/t2d fits (W3a Route L); coloc.susie is run for the 9 SH2B3 canonical pairs with the R2 coloc script and its R2-era priors (D-17)"
    - "The comparison against results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json records PP.H4 per pair, the fingerprint (bmi-hypertension n_cs 13 x 5, nsnps 168, hit rs3184504), the L15 n_CS (13/5/3) and ld_overlap (170/589/622) for bmi/htn/stroke"
    - "The standard L=10 / iter-100 SH2B3 run (Route C fits) is reported as a SEPARATE measurement, never as the known answer (D-17)"
    - "A findings report consolidates every known-answer result from W2a/W2b/W3a/W3b with mismatches stated as findings; Carter reviews it at a checkpoint:human-action (auto-mode stops) and his reply is recorded only if it parses as `carter-approved YYYY-MM-DD` + `instructions:` (B1)"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md"
      provides: "known-answer findings report (input to the W4a amendment)"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/known_answer_sh2b3.tsv"
      provides: "per-pair SH2B3 reproduction table (R2 config and L10/iter-100 rows, labelled)"
  key_links:
    - from: "ta-r4-W3-KNOWN-ANSWER-FINDINGS.md"
      to: "W4a OSF amendment §(h) known-answer results"
      via: "copied numbers with source table paths"
      pattern: "known_answer_"
---

<objective>
Wave 3b reproduces the SH2B3 PP.H4 = 1.0 known answer in its true configuration (D-17). It reports
the standard L=10 / iter-100 run separately. It consolidates every known-answer result into one
findings report, which Carter reviews before the pre-registration is finalized.

Purpose: D-12(b) as corrected by D-17; feeds the W4a amendment.
Output: SH2B3 repro fits + coloc outputs on /rs1, a comparison table, the findings report, Carter's sign-off.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3a-known-answer-routes-SUMMARY.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-canonical-pair-coloc-susie-SUMMARY.md

<interfaces>
R2 provenance (research Pitfall 1; verify line numbers): ta-sh2b3-W2-canonical-pair-coloc-susie-SUMMARY.md:45,102,153-156
R2 outputs (tracked): results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__{asthma_vs_bmi,asthma_vs_hypertension,asthma_vs_stroke,
  bmi_vs_hypertension,bmi_vs_stroke,bmi_vs_t2d,hypertension_vs_stroke,hypertension_vs_t2d,stroke_vs_t2d}.json
  + .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv
R2 fire tooling: bin/fire_canonical_susie_pairs.sh, config/pipeline_canonical_r2_overlay.yaml, config/pipeline_lsweep_L15_overlay.yaml,
  config/susie_policy_L15.yaml (and *.preNiter500.bak.* = the earlier 100-iter version)
L-sweep known answers: ta-sh2b3-W1-convergence-report.tsv (niter 1000: L15 13/5/3) and -niter100.tsv
Surviving lsweep JSONs (ld_overlap 170/589/622): data/r4/known_answer_survivors/results_lsweep_L15.preNiter500.bak.20260429_213644/
Expected R2 values: bmi-htn 1.0 (rs3184504, nsnps 168, n_cs 13 x 5); htn-stroke 1.0; htn-t2d 1.0; bmi-t2d 4.3e-27; stroke-t2d 0
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Identify the R2-fire code commit; wire and fire the SH2B3 R2-exact and L10/iter-100 measurements</name>
  <files>src/snakemake/rules/ta_r4_repro.smk, src/snakemake/rules/ta_r4_finemap.smk, src/python/ta_r4/commands.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_repro_sh2b3_sha256.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/legacy_code_sha256.tsv</files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-canonical-pair-coloc-susie-SUMMARY.md (whole; record the exact lines that state which fits were swapped in)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-*-SUMMARY.md (the lsweep fire commit and policy)
    - bin/fire_canonical_susie_pairs.sh, bin/fire_susie_lsweep.sh, config/pipeline_canonical_r2_overlay.yaml, config/susie_policy_L15.yaml
    - `git log --format='%h %ad %s' --date=iso -- src/legacy/region_analysis/scripts/run_susie_rss.R src/snakemake/scripts/run_coloc_susie.R | head -30`
  </read_first>
  <action>
    1. From the SUMMARYs and git log, determine:
       (a) the commit at which the L15 lsweep fits that R2 used were produced;
       (b) the policy file content then (via `git show <ref>:config/susie_policy_L15.yaml`);
       (c) the commit and coloc script used for the R2 coloc.
       Record each with its evidence line in the LOG. Extract code at (a) and (c) with
       `bin/r4_extract_legacy_code.sh <ref>` (it records sha256 rows).
    2. Add to `ta_r4_repro.smk` (arm `repro_sh2b3_r2`):
       - L15 fits for bmi, hypertension and stroke EUR at SH2B3, using the code at (a), the policy
         at (b) (written to `data/r4/legacy_code/<ref>/config/susie_policy_L15.yaml`), the
         legacy_repro panel, the legacy catalog and legacy semantics.
       - Rule `r4_sh2b3_r2_coloc`: the coloc script at (c) for the 9 canonical pairs, with
         bmi/htn/stroke from the L15 fits and asthma/t2d from `repro_routeL` (Stage-2 L10). Output
         `data/r4/results/repro_sh2b3_r2/coloc/<pair>.json`.
       - Rule `r4_sh2b3_L10_coloc`: the same coloc script on the `repro_routeC` L10 / iter-100
         fits for all 5 traits. Output `data/r4/results/repro_sh2b3_L10/coloc/<pair>.json`.
       All of this is stage repro, so no gate applies. If the L15 fits need a policy path or option
       the W0c/W3a `commands.fit_command` legacy branch does not support, extend that branch (and
       `ta_r4_finemap.smk` only if its shell must change); the W0c e2e and W0d toy e2e tests must
       stay green. Otherwise leave both files untouched and say so.
    3. Dry-run, fire (serial queue; L15 at 1000 iterations may take ~30 min per fit), confirm
       "Nothing to be done" afterwards, and write the sha256 manifest of fits + coloc outputs.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && ls data/r4/results/repro_sh2b3_r2/coloc/*.json | wc -l && ls data/r4/results/repro_sh2b3_L10/coloc/*.json | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - both counts print 9
    - the LOG names the commits (a) and (c) and the policy (b) max_iter values, each with a quoted evidence line and its file:line
    - `$MAN/fits_repro_sh2b3_sha256.tsv` covers 3 fit JSONs + 3 fit.rds + 18 coloc JSONs = 24 rows (arithmetic pasted)
  </acceptance_criteria>
  <done>The SH2B3 R2-exact configuration and the L10/iter-100 measurement have both run.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: SH2B3 comparison table + findings report; wave-close (W3b)</name>
  <files>src/python/ta_r4/sh2b3_known_answer.py, tests/ta_r4/test_sh2b3_known_answer.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/known_answer_sh2b3.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json (key names for PP.H4, nsnps, hit, n_cs)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv
    - manifests/known_answer_W3a.tsv; data/r4/findings/*.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-trait-pair-coloc-refire-SUMMARY.md (lines 20-70; the 28 R1 rows) and ta-r3-W2-r1-targets.tsv
  </read_first>
  <behavior>
    - The table has exactly 18 rows: 9 pairs × {R2_exact, L10_iter100}; config_label is the column that distinguishes them
    - Per row: pp_h4_reproduced, pp_h4_frozen (R2 JSON; NA for L10 rows), abs_diff, nsnps, hit1, hit2, n_cs_a, n_cs_b, and match_flag (|diff| ≤ 1e-6 and equal fingerprint) for R2_exact rows only
    - The fingerprint check for bmi_vs_hypertension compares n_cs 13 × 5, nsnps 168 and hit rs3184504 field by field
    - Unit tests on synthetic JSON pairs; the live test (marked r4_heavy; skips only while the repro_sh2b3_r2 dir is absent) asserts the table has 18 rows built from files on disk. It does NOT assert match (§B.10)
  </behavior>
  <action>
    1. Tests RED, then implement `sh2b3_known_answer.py`. Write `$MAN/known_answer_sh2b3.tsv`.
       Also compare the reproduced L15 n_CS and ld_overlap for bmi/htn/stroke against 13/5/3 and
       170/589/622, with sources cited.
    2. Write `ta-r4-W3-KNOWN-ANSWER-FINDINGS.md`. Sections:
       (1) panels (from W2a/W2b findings: EUR n, SH2B3 895, |R| equality, AFR / UKB sizes, UKB sign agreement);
       (2) Route C vs Route L agreement counts;
       (3) k2d per-fit agreement;
       (4) Stage-2 aggregate reproduction;
       (5) SH2B3 R2-exact per-pair reproduction plus the fingerprint;
       (6) SH2B3 L10/iter-100, labelled "separate measurement — not the known answer";
       (7) the implications to state in the amendment, in one line each;
       (8) the R1_STRUCTURAL re-examination (ROADMAP scope): the measured cause of the 28 empty R1
           trait-pair rows, quoted with file:line from
           `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-trait-pair-coloc-refire-SUMMARY.md`
           (line 25: 28 R1 JSONs re-fired, `status="no_signal"`, `n_cs_a=0 OR n_cs_b=0`; line 66:
           per-JSON failure mode, SuSiE-RSS attrition cascading to coloc.susie no_signal; verify both
           line numbers by reading the file), cross-checked against the Route C / Route L n_CS of the
           underlying fits in `known_answer_W3a.tsv` (count of the 28 pairs with n_CS = 0 on ≥ 1 side,
           reconciled to 28), and the statement that D-02 (`fallback_abf`, labelled, with the per-arm
           no-CS rate reported as E4) is the pre-specified handling of that case.
       Every number is pasted with its source path. Mismatches are stated as findings, with no
       remediation proposed that would adjust numbers.
    3. Run §C with label `W3b`, commit type `test`.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_sh2b3_known_answer.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - the test passes with the live test run; `awk 'NR>1' $MAN/known_answer_sh2b3.tsv | wc -l` prints 18
    - the findings report has the 8 sections, and every number in it carries a source path; §(8) quotes the ta-r3-W2 SUMMARY lines with file:line
    - committed with explicit paths; pushed
  </acceptance_criteria>
  <done>The SH2B3 known answer is measured in its true configuration, and all findings are consolidated.</done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 3: Carter reviews the known-answer findings before the pre-registration is drafted (human-action; auto-mode cannot pass it)</name>
  <what-built>Reproduction of the frozen Track A fits by two routes, the k2d identity fits, the SH2B3 R2-exact configuration and the L10/iter-100 measurement, consolidated in `ta-r4-W3-KNOWN-ANSWER-FINDINGS.md` with committed tables.</what-built>
  <how-to-verify>
    1. Read `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md`.
    2. Confirm that each mismatch is stated as a finding (not adjusted), and that the SH2B3 provenance statement is the one you want in the amendment and manuscript (D-17).
    3. Say whether any finding changes the pre-registration draft (W4a).
  </how-to-verify>
  <resume-signal>Carter replies with the first line exactly `carter-approved YYYY-MM-DD`, then `instructions: <text or none>`. Any other reply, including a bare "approved", means WAIT: re-present this checkpoint and record nothing.</resume-signal>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/W3b-T3.yaml, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <action>
    Sign-off integrity (§B.15): the executor never authors, types or completes any
    `carter-approved` text and never writes signoffs/*.yaml except via `python -m ta_r4.signoff record`.
    The raw file is written only from the resume payload the orchestrator passes, which must be
    Carter's message pasted verbatim (never a summary, paraphrase or auto response). The SUMMARY
    quotes the resume payload next to the recorded raw_sha256.

    Present the report. Save the reply byte-for-byte to `data/r4/tmp/signoff_W3b-T3.txt` and run
    `cd src/python && $PY -m ta_r4.signoff record W3b-T3 --raw-file ../../data/r4/tmp/signoff_W3b-T3.txt --min-date <date of the W3b commit>`.
    Non-zero exit → WAIT (print the message, re-present, write nothing). Never construct a reply
    or log an auto-generated response as Carter's sign-off. On success, append the reply verbatim
    to the LOG with its date, commit the sign-off file and the LOG with explicit paths, and push.
  </action>
  <verify><automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.signoff verify W3b-T3 && echo SIGNED_OFF</automated></verify>
  <acceptance_criteria>
    - `signoff verify W3b-T3` exits 0; the LOG has a dated entry quoting Carter's reply verbatim
    - the SUMMARY quotes the resume payload verbatim next to the recorded raw_sha256
  </acceptance_criteria>
  <done>Carter has reviewed the known-answer findings; W3c starts only after `signoff verify W3b-T3` passes.</done>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md
  </read_first>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| a historical "known answer" → a public claim | a mis-specified premise (the L=15 swap) could be propagated into the manuscript |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W3b-01 | Repudiation | SH2B3 provenance | mitigate | the R2-exact configuration is reproduced from extracted commits with sha256; L10 is labelled separately; Carter signs off |
| T-r4-W3b-02 | Tampering | tuning toward 1.0 | mitigate | the table is committed as produced; no policy change in this plan; §B.10 |
| T-r4-W3b-03 | Elevation of privilege | auto-approval | mitigate | `checkpoint:human-action`; `carter-approved YYYY-MM-DD` token parsed by ta_r4.signoff; W3c checks `signoff verify W3b-T3` before starting |
</threat_model>

<verification>
18-row SH2B3 table. The findings report is complete, with sources. Carter's sign-off is recorded.
</verification>

<success_criteria>
The SH2B3 "PP.H4 = 1.0" claim has a measured, correctly attributed provenance, and every
known-answer finding is in front of Carter before pre-registration.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3b-sh2b3-known-answer-and-findings-SUMMARY.md`
</output>
