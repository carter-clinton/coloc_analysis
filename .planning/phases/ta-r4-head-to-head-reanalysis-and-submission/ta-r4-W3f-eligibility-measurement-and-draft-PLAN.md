---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.5
slug: W3f-eligibility-measurement-and-draft
type: execute
wave: 15.5
depends_on: ["ta-r4-W3f-reporting-widening-qtl-sim"]
gap_closure: true
files_modified:
  - src/python/ta_r4/measure_fit_eligibility.py
  - tests/ta_r4/test_measure_fit_eligibility.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_region_contribution_proxy.tsv
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - tests/ta_r4/test_amendment_text.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-SUSIE-RSS-POLICY
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "The after-fix early-exit count is measured, not assumed: panels with <= 16,000 variants cannot early-exit (post-restriction n <= panel n_var), and every panel above 16,000 is measured with the fixed producer in a no-fit mode (cap 0, outputs only under data/r4/tmp/w3f) — the ~35 previously early-exiting primary rows are re-counted"
    - "No production fit is run: every measurement output is an early-exit JSON whose RDS has no lbf_variable, written only under data/r4/tmp/w3f"
    - "How many of the 10 confirmatory regions are likely to contribute both_have_cs rows is reported per contrast from existing pre-lock fits (labelled a proxy); if fewer than 7 is likely, it is a flag for Carter and the floor is not lowered"
    - "The DRAFT states every changed behaviour (status gate, input sha256 in-job, the fit-name and early-exit rules replacing their CARTER-LOCK placeholders, sign-flip test and n_regions_min with its 2/2^k justification, E4/E6 widened, completeness/coverage refusal, simulation policy, cap stage, QTL fallback export, frozen paths, W3f commit shas)"
    - "confirmatory_sha256 is recomputed and recorded old f6e6e90f... -> new; test_amendment_text passes"
  artifacts:
    - path: "src/python/ta_r4/measure_fit_eligibility.py"
      provides: "argv rewrite of commands.fit_command to cap 0 + tmp output; refuses result dirs; summarise() over outputs"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv"
      provides: "per (arm, trait, ancestry, region): panel n_var, n_variants_pre_ld, n_variants post, eligible, method (bound|measured)"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_region_contribution_proxy.tsv"
      provides: "per confirmatory region and contrast: proxy pairs with CS on both sides, classification likely|unknown|unlikely"
    - path: ".planning/amendments/osf-amendment-r4-DRAFT.md"
      provides: "DRAFT matching the W3f code; new confirmatory_sha256 in the Pre-Paste reference"
  key_links:
    - from: "src/python/ta_r4/measure_fit_eligibility.py"
      to: "src/python/ta_r4/commands.py::fit_command"
      via: "same argv except SUSIE_MAX_VARIANTS=0, absolute Rscript and a data/r4/tmp/w3f output"
      pattern: "fit_command"
---

<objective>
W3f fix-up, plan 5 of 6: measure what the fixes changed (N1 recount; N7 contributing-region count) without
running production, then make the DRAFT describe the code exactly and recompute `confirmatory_sha256`.

Purpose: Carter locks against the DRAFT and the sha; both must describe the code that will run, and the
region floor's practical consequence must be visible to him before he locks it.
Output: eligibility and region-contribution manifests, the measurement module with tests, the updated DRAFT,
the new sha.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md
@.planning/amendments/osf-amendment-r4-DRAFT.md

Standing rules: PLAN-INDEX §A/§B/§C. Slurm only (memory feedback_slurm_not_lsf): `sbatch -p compute -A clintonlab_cpu
-q normal -t <limit>` (always -t), Rscript is not on PATH in jobs — use $RSCRIPT absolute. Do NOT run production fits,
do NOT invoke bin/r4_fire.sh, do NOT write under data/r4/results. Public-text rules (§B.11) and the internal-content
scan apply to every DRAFT edit inside the PASTE block.

Measured at planning time (panel manifests, `n_var`): every EUR 1000G, identity and intersection panel is
<= 15,236 variants (max PYHIN1_1q23); panels above 16,000: AFR661_1kg / AFR661_identity / AFR504_1kg at
BMI_5q13_3 (21,154-21,323) and PYHIN1_1q23; EUR_ukb337k native at BMI_5q13_3, PYHIN1_1q23, SLC2A9_urate and
HLA_6p21 (inadmissible). Re-derive these from the manifests; do not copy them.

<interfaces>
src/python/ta_r4/commands.py: fit_command(arm, trait, ancestry, region_safe, config, *, region_id=None) -> argv
  ["env", "SUSIE_MAX_VARIANTS=16000", "Rscript", script, ..., "--cap-after-ld-restriction", "true", ..., "--output", fit_json]
  (config = the merged pipeline.yaml + overlay_base + overlay_<arm> dict, as the e2e tests build it)
run_susie_rss.R under the flag: post-restriction early exit writes JSON status too_many_variants with n_variants (post), n_variants_pre_ld, cap_stage, and an RDS without lbf_variable
src/python/ta_r4/paths.py: result_dirs("fits"|"coloc"), panel_manifest_path(arm, ancestry), fit_rds/fit_json
Existing pre-lock fits: data/r4/results/repro_routeC|repro_routeL|repro_k2d_routeC|repro_k2d_routeL/fine_mapping/susie/*.fit.rds (+ .json); $MAN/fit_cs_json_vs_rds.tsv (n_cs_rds_sets); $MAN/known_answer_W3a.tsv
src/python/ta_r4/signoff.py: canonical_sha256(obj)
src/python/ta_r4/extract_paste_block.py: extract(path), render_confirmatory(rules); CLI --in --out
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Measure after-fix fit eligibility (no-fit mode, Slurm) and the confirmatory-region contribution proxy</name>
  <files>src/python/ta_r4/measure_fit_eligibility.py, tests/ta_r4/test_measure_fit_eligibility.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_region_contribution_proxy.tsv</files>
  <read_first>
    - src/python/ta_r4/commands.py, src/python/ta_r4/paths.py, src/python/ta_r4/arms.py (production arms and their panels)
    - tests/ta_r4/test_frozen_script_armed_e2e.py (how the merged config dict is built for fit_command)
    - $MAN/panels_*_r4.tsv (n_var), config/ta_r4/pair_manifest.tsv (primary admissible rows), $MAN/fit_cs_json_vs_rds.tsv
    - the review's N1 table (asthma/T2D pre-restriction counts) and the W4a disposition (asthma x PYHIN1 38,313)
  </read_first>
  <behavior>
    - measurement_argv(arm, trait, ancestry, region_safe, config, out_dir, rscript): equals fit_command(...) except SUSIE_MAX_VARIANTS=0, "Rscript" -> rscript, --output -> <out_dir>/<arm>/<trait>.<ancestry>.<region>.json; raises if out_dir is not under data/r4/tmp/ or if the output path lies in any paths.result_dirs(...) directory, or if --cap-after-ld-restriction true is absent
    - summarise(out_dir) -> rows (arm, trait, ancestry, region_safe, status, n_variants_pre_ld, n_variants, cap_stage); raises if any RDS has lbf_variable (a fit happened) or any status is not an early exit
    - eligibility rule: eligible = n_variants (post-restriction) <= 16000; for panels with n_var <= 16000, method = "bound" (n_variants <= n_var <= 16000) and no run is needed
  </behavior>
  <action>
    1. RED → GREEN for measurement_argv / summarise (unit tests, not heavy; one r4_heavy test runs the no-fit mode on
       the tiny e2e fixture and checks the RDS has no lbf_variable). Negative control: let measurement_argv keep
       SUSIE_MAX_VARIANTS=16000 → the cap-0 assertion fails (paste).
    2. Build the run list: every (production arm, trait, ancestry, admissible region) whose panel n_var > 16000
       (re-derived from the manifests), plus the regression pair asthma x PYHIN1_1q23 and t2d x PYHIN1_1q23 under
       A3_1kg (bound case, measured as a check that n_variants <= panel n_var and n_variants_pre_ld > 16000).
       Print the list length. Write the driver to data/r4/tmp/w3f/elig/run.sh and submit one Slurm array:
       `sbatch -p compute -A clintonlab_cpu -q normal -t 01:00:00 --mem=32G --array=1-<N> data/r4/tmp/w3f/elig/run.sh`.
       Wait for completion by output listing (one JSON per task), not job state. Any task without a JSON: read its log,
       report, re-run once; still failing = STOP and report.
    3. Write $MAN/w3f_fit_eligibility.tsv: one row per (production arm, trait, ancestry, admissible region) — measured
       rows from summarise(), every other row with method "bound" and its panel n_var. Re-count the primary rows:
       previously early-exiting rows (the review's 35; reconcile your own pre-fix count from n_variants_pre_ld > 16000
       on both regression traits + the review table) → after-fix count of primary EUR rows with either trait not
       eligible under A3_1kg or A2_identity (expected 0 by the bound; state the number), and separately for A3_ukb
       native and the AFR arms. Paste the counts and their reconciliation (rows = sum of parts) into the LOG.
    4. Region-contribution proxy (no new fits): for each of the 10 confirmatory regions, from existing repro fits,
       count EUR trait pairs with ≥ 1 purity-filtered credible set (fit RDS `sets$cs`) on both traits under
       repro_routeC (proxy for A3 → A1_matched_vs_A3_1kg both_have_cs) and under both repro_routeC and
       repro_k2d_routeC (proxy for A2_identity_vs_A3_1kg). A region whose repro fits early-exited or are absent is
       "unknown"; ≥ 1 qualifying pair = "likely"; 0 = "unlikely". Write $MAN/w3f_region_contribution_proxy.tsv
       (region, contrast, n_pairs_both_cs_proxy, n_pairs_unknown, classification, source_arms) and the per-contrast
       totals. State the proxy's limits in the LOG (earlier panels and policies, pre-orientation-fix joins, pre-fix cap;
       never an input to any lock value). If "likely" < 7 for either contrast, write
       `FLAG FOR CARTER: n_regions_min 7 may yield NON_INFORMATIVE for <contrast> (likely <n>/10, unknown <m>)`
       in the LOG; do not change n_regions_min.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_measure_fit_eligibility.py -q -rs && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import csv; r=list(csv.DictReader(open('.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv'),delimiter='\t')); print(len(r), sum(x['method']=='measured' for x in r), sum(x['eligible']=='false' for x in r))"</automated>
  </verify>
  <acceptance_criteria>
    - tests pass; NC pasted
    - every measured RDS lacks lbf_variable (summarise() raised nothing); no file was written under data/r4/results (`find -L data/r4/results -newer data/r4/tmp/w3f/elig/run.sh -type f | wc -l` prints 0)
    - the asthma x PYHIN1_1q23 A3_1kg row shows n_variants_pre_ld > 16000 and n_variants <= the panel n_var (both numbers pasted)
    - the LOG states the pre-fix and after-fix early-exit row counts with arithmetic reconciliation, and the per-contrast likely/unknown/unlikely region totals (sum = 10 per contrast), plus the FLAG line if triggered
  </acceptance_criteria>
  <done>The fixes' effect on fit eligibility and the region floor's likely consequence are measured and on record before Carter locks.</done>
</task>

<task type="auto">
  <name>Task 2: Update the DRAFT for every changed behaviour</name>
  <files>.planning/amendments/osf-amendment-r4-DRAFT.md, tests/ta_r4/test_amendment_text.py</files>
  <read_first>
    - .planning/amendments/osf-amendment-r4-DRAFT.md (whole: Pre-Paste reference, PASTE block, Post-Paste)
    - the SUMMARYs of plans 15.1–15.4 (exact behaviours, commit shas) and Task 1's LOG entry
    - config/ta_r4/decision_rules.yaml; src/python/ta_r4/r4_lock_gate.py LOCKED_PATHS; tests/ta_r4/test_amendment_text.py
  </read_first>
  <action>
    Edit only what changed; keep the existing wording elsewhere. Inside the PASTE block:
    1. Status paragraph: the gate is checked when a production run is constructed and again as the first step of
       every production job.
    2. (c): inputs' sha256 are recorded before production and verified inside every production fit, colocalization
       and QTL job; a mismatch or an unlisted input fails the job.
    3. (d): replace both ‹CARTER-LOCK› placeholders. Early-exit rule: fits that exit before fitting (no variants, or
       more than 16,000 variants after restriction to the panel) and pairs for which coloc.susie returns no summary or
       no finite PP.H4 are kept as rows with method `none` and a recorded reason, excluded from the both-have-CS
       subset, and counted in a reported drop table. Fit-name rule: a fit variant name that is not a summary-statistic
       identifier is looked up in the variant table of the LD panel the fit used and matched by position with an
       allele check (exact, swapped, or the strand complement of either for non-palindromic SNVs; palindromic or
       ambiguous matches are unmapped); any unmapped name stops the pair with an error, so no variant is dropped silently.
    4. (e): E2's McNemar test is descriptive; E4 as now implemented (every fit with credible sets whatever its status;
       the native and intersection UK Biobank/1000 Genomes pairs in both directions, A2 vs A3, and the AFR analogues;
       no-credible-set rate per pair row, per region and per fit, each with its denominator); E6 = E1–E5 on each
       sensitivity contrast with drop counts; classification refuses unless every confirmatory row has an output in
       both arms, and final tables are written only when colocalization coverage is exact (no missing or extra
       outputs). The rendered confirmatory block from plan 15.3 stays verbatim.
    5. (f): NON_INFORMATIVE when n_both < n_both_min or fewer than n_regions_min = 7 regions contribute a both-have-CS
       row; the direction category (named `mcnemar` in the rules) is decided by the exact region-level sign-flip test
       (state d_r, T, the 2^k enumeration, the Monte Carlo rule above k = 20, two-sided, alpha); justification: the
       smallest attainable two-sided p is 2/2^k, so 6 regions (0.03125) cannot reach alpha = 0.025 and 7 (0.015625) can.
       Keep the 36-combination counts (unchanged; re-derive them from enumerate_truth_table and confirm).
    6. (g): no R = I refit (a fit the ladder cannot produce gives that arm's replicate method `none`); rates per method,
       never pooling `coloc_susie` and `fallback_abf`; aggregation requires all 100 cells with the configured replicates.
    7. (k): the 16,000-variant cap applies after restriction to the panel; with the measured panel sizes no
       confirmatory fit can reach it (largest EUR 1000G panel, from Task 1); state the measured count of A3-UKB and AFR
       fits above it (from Task 1) as method-`none` rows.
    8. (l): QTL rows with no credible set are exported with method `fallback_abf` and their posteriors in the aggregate
       table and excluded from tiering by an explicit method filter.
    9. (m): frozen paths = LOCKED_PATHS (already synced in plan 15.2; re-check), analysis-code commits extended with the
       W3f code commits from plans 15.1–15.4 (short shas from the LOG).
    Outside the PASTE block (Pre-Paste reference): proposed lock values now include `n_regions_min: 7` (inside the
    confirmatory block, bound by confirmatory_sha256); add the Task 1 region-contribution result and the FLAG line if
    raised. No internal paths, `.planning/`, `data/r4` or checklist items inside the PASTE block; no framing-banned words.
    Run test_amendment_text.py; record the extract word count (target ≤ ~3,100; report the number either way).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py -q -rs && cd src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "from ta_r4.extract_paste_block import extract; t=extract('../../.planning/amendments/osf-amendment-r4-DRAFT.md'); print(len(t.split()), t.count('CARTER-LOCK: early-exit'), t.count('CARTER-LOCK: fit-name'))"</automated>
  </verify>
  <acceptance_criteria>
    - test_amendment_text.py passes
    - the extract contains no `CARTER-LOCK: early-exit` or `CARTER-LOCK: fit-name` placeholder (both counts print 0); the other lock placeholders remain
    - each of the nine edits is listed in the SUMMARY with the code behaviour it describes (file:function) — one row per item N1–N14/T1 touched
  </acceptance_criteria>
  <done>The DRAFT describes the code that will run, with the two decided rules written out.</done>
</task>

<task type="auto">
  <name>Task 3: Recompute confirmatory_sha256; commit, push, LOG</name>
  <files>.planning/amendments/osf-amendment-r4-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <read_first>
    - config/ta_r4/decision_rules.yaml; src/python/ta_r4/signoff.py (canonical_sha256); the plan 15.3 LOG entry (interim sha)
  </read_first>
  <action>
    1. `cd src/python && $PY -c "import yaml; from ta_r4.signoff import canonical_sha256; print(canonical_sha256(yaml.safe_load(open('../../config/ta_r4/decision_rules.yaml'))['confirmatory']))"`.
       It must equal the plan 15.3 interim value (plans 15.4–15.5 do not touch the confirmatory block); if not, find why
       and report before continuing. Write `old f6e6e90f83fd14975d3afa04789c3dcf1a9211b8e3ddd38bf23c72f8cbe0e9e3 → new <hex>`
       into the DRAFT's Pre-Paste reference (outside the PASTE block) and the LOG.
    2. §C: $QUICK (wall time), pins file. `git fsck`; explicit-path commit of the measurement module, its test, the two
       manifests and the DRAFT (`docs(ta-r4-W3f): eligibility + region-contribution measurement; DRAFT matches W3f code; confirmatory_sha256 <short>`);
       `git fsck`; push. LOG entry (Task 1 counts, DRAFT edit list, word count, old → new sha, QUICK time); refresh the W3f progress line in STATE.md (§C); commit LOG and STATE.md; push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git status --porcelain -- .planning/amendments/osf-amendment-r4-DRAFT.md src/python/ta_r4/measure_fit_eligibility.py && git log origin/m3-W2-aou-deltas..HEAD --oneline | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - the recomputed sha equals the interim sha from plan 15.3 (both printed in the LOG)
    - porcelain is empty for the committed files and `git log origin/m3-W2-aou-deltas..HEAD` count prints 0
  </acceptance_criteria>
  <done>The new confirmatory_sha256 Carter will confirm is recorded next to the old one, and the DRAFT is pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| measurement → production | a measurement must not become an unlocked production run |
| DRAFT → public record | the DRAFT becomes public text after W4b |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W3f5-01 | Elevation of privilege | measure_fit_eligibility | mitigate | cap 0 forced; tmp-only output; result-dir refusal; summarise() raises on any fitted RDS; no r4_fire.sh |
| T-r4-W3f5-02 | Information disclosure | DRAFT PASTE block | mitigate | internal-content and framing scans over the whole extract (test_amendment_text) |
| T-r4-W3f5-03 | Repudiation | lock target | mitigate | old → new confirmatory_sha256 recorded with the command that produced it |
</threat_model>

<verification>
Eligibility and region-contribution manifests exist with reconciled counts; no production output was written; the
DRAFT passes its text tests and the new sha is recorded.
</verification>

<success_criteria>
Carter can lock against a DRAFT and sha that match the code, with the floor's practical consequence measured.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-eligibility-measurement-and-draft-SUMMARY.md`
</output>
