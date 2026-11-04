---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.1
slug: W3f-producer-cap-fit-names-early-exit
type: execute
wave: 15.1
depends_on: ["ta-r4-W3e-qtl-harmonize-and-group-runner"]
gap_closure: true
files_modified:
  - .planning/DECISIONS.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-decisions-2026-11-04.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-n1-unfreeze-reply.txt
  - src/legacy/region_analysis/scripts/run_susie_rss.R
  - src/python/ta_r4/commands.py
  - src/python/ta_r4/estimands.py
  - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R
  - src/snakemake/rules/ta_r4_coloc.smk
  - tests/m3/test_source_freeze_pins.py
  - tests/ta_r4/test_cap_after_panel.py
  - tests/ta_r4/test_fit_name_alignment.py
  - tests/ta_r4/test_coloc_none_states.py
  - tests/ta_r4/test_coloc_pair_r4.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-SUSIE-RSS-POLICY
  - REQ-SNAKEMAKE-CI
  - REQ-PATH-PARAMETERIZATION

must_haves:
  truths:
    - "Carter's 2026-11-04 W3f decisions are recorded byte-for-byte as DEC entries before any code changes (fix all; N7 do both)"
    - "The run_susie_rss.R edit for N1 happens only after a DEC quotes Carter's explicit N1 unfreeze reply verbatim; without it the plan stops before touching the frozen script"
    - "Under --cap-after-ld-restriction true the 16,000-variant cap is applied to the panel-restricted subset; a catalog-joined subset above the cap whose panel-restricted subset is within the cap is fitted, not skipped (Codex N1)"
    - "Without the flag the frozen script behaves as at 53106f8 (Track B, repro arms and the simulation harness unchanged, D-15); every non-legacy R4 fit argv passes the flag"
    - "Fit variant names are aligned to summary statistics through the LD panel the fit was built against, with an allele check; any unmapped name is a hard error naming the count and the first examples (Codex N2), in --mode susie, A1_matched and qtl_abf"
    - "repro_routeC SH2B3_12q24 hypertension x stroke goes from UNMAPPED_FIT_NAMES 589/589 to 0 unmapped"
    - "Early-exit fits, an empty coloc.susie summary and a summary with no finite PP.H4 produce a written coloc output with method none and an explicit none_reason, never a crash; method none rows are never both_have_cs (Codex N8)"
  artifacts:
    - path: "src/legacy/region_analysis/scripts/run_susie_rss.R"
      provides: "--cap-after-ld-restriction flag (default false); early-exit JSON/RDS record n_variants_pre_ld and cap_stage under the flag"
    - path: "src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R"
      provides: "map_fit_names() panel-mediated alignment; --ld-panel; method none outputs with none_reason"
    - path: "tests/ta_r4/test_fit_name_alignment.py"
      provides: "allele-check cases, hard-error message, SH2B3 real-data regression"
    - path: "tests/m3/test_source_freeze_pins.py"
      provides: "R_CODE_REF re-pinned to the N1 code commit"
  key_links:
    - from: "src/python/ta_r4/commands.py::fit_command"
      to: "run_susie_rss.R --cap-after-ld-restriction"
      via: "argv for every non-legacy arm on CURRENT_SCRIPT"
      pattern: "--cap-after-ld-restriction"
    - from: "src/python/ta_r4/commands.py::coloc_command"
      to: "run_coloc_pair_r4.R --ld-panel"
      via: "paths.panel_path(arm, region_safe, ancestry) for modes susie and A1_matched"
      pattern: "--ld-panel"
    - from: "src/python/ta_r4/estimands.py::region_stat"
      to: "method none rows"
      via: "returns (nan, False); both_have_cs is false by construction"
      pattern: "none"
---

<objective>
W3f fix-up, plan 1 of 6: the producer-side production blockers found by the brief-blind review
(`ta-r4-W4-AMENDMENT-REVIEW-as-received.md` N1, N2, N8), plus the DEC record of Carter's decisions.

Purpose: without N1 ~35 primary rows hit FIT_EARLY_EXIT; without N2 most EUR pairs refuse with
UNMAPPED_FIT_NAMES; without N8 three outcome states crash instead of being reported. Each blocks the
confirmatory analysis from running as written.
Output: flag-gated cap move in the frozen script (D-28 lifted once more, scoped by DEC), panel-mediated
fit-name alignment, method `none` outputs, tests with observed RED and negative controls, R_CODE_REF re-pin.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md

Standing rules: PLAN-INDEX §A constants ($REPO, $P, $MAN, $PY, $RSCRIPT, $QUICK, $HEAVY, $FULL), §B
(explicit-path staging; RED first with observed negative controls; behaviour not text; a count is a claim;
no branch switching), §C wave close. §B.6 (D-28) is lifted ONLY by the unfreeze DEC written in Task 2 step 0 from Carter's explicit reply, and only for its scope.
Memory rules: feedback_green_assertion_needs_a_negative_control, feedback_grep_gate_matches_text_not_meaning,
feedback_fix_the_producer_not_just_the_consumer, feedback_check_plan_against_red_before_executing,
feedback_keep_edits_simple_no_superfluous_prose, reference_gpfs_git_object_store_loss, feedback_multi_terminal_staging.
R in tests: use $RSCRIPT (absolute path); tests that run Rscript or read data/r4/results are marked `r4_heavy`
so $QUICK stays < 120 s.

<interfaces>
Frozen script src/legacy/region_analysis/scripts/run_susie_rss.R (code-pinned; tests/m3/test_source_freeze_pins.py
R_CODE_REF = "53106f8", "update exactly one constant" on an authorized code change):
  :681   make_option("--ld-authoritative", type = "character", default = "true", ...)  # strict true/false parsing pattern to copy
  :711   SUSIE_MAX_VARIANTS <- as.integer(Sys.getenv("SUSIE_MAX_VARIANTS", "6000"))
  :946   if (nrow(subset) > SUSIE_MAX_VARIANTS) { ...status = "too_many_variants"...; saveRDS(list(status, region, n_variants, limit), fit_rds_path); quit(status = 0) }
  :981   repeat { ld_result <- load_ld_matrix(opt$`ld-dir`, ..., subset, ..., ld_file = opt$`ld-file`) ...retry may reset subset <- copy(subset_base) }
         (ONE LINE, ld_file LAST: tests/m3/test_ld_read_path.py::T2.2 matches this call with a single-line regex)
  :1037  assert_declared_ld_authoritative(...)
  :1041  if (!is.null(ld_result$subset_idx)) subset <- subset[ld_result$subset_idx]       # the panel restriction
  :1052  rsid override: subset[replace_mask, SNP_ID := ld_ids[replace_mask]]

src/python/ta_r4/commands.py:
  SUSIE_MAX_VARIANTS = 16000; CURRENT_SCRIPT from ta_r4.arms
  fit_command(arm, trait, ancestry, region_safe, config, *, region_id=None) -> argv (adds --ld-file/--ld-authoritative/--ld-allele-aware when script == CURRENT_SCRIPT)
  coloc_command(arm, row, p12_key, mode) -> argv (modes susie, A1_matched, A1_allvars)
  _legacy(arm) = ARMS[arm]["validator_mode"] == "legacy_any"

src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R:
  read_region(path, reg) -> ss (CHR, POS, REF, ALT, SNP_ID, cp = "CHR:POS", name = SNP_ID else cp)
  main(): align_names(fit, ss, label) [fails UNMAPPED_FIT_NAMES]; load_fit(path, ss, label) [fails FIT_EARLY_EXIT when no lbf_variable]
  coloc_pair_core(fa, fb, ti_a, ti_b, pri, mode, labels) -> list(method, pp, r, out) [fails COLOC_SUSIE_EMPTY on NULL summary];
    source()d by simulate_coloc_r4.R (W3c): keep its signature and return shape
  qtl_abf_main(opt): idx <- match(b$snps, ss$name) [same UNMAPPED failure class; --ld-matrix is the GWAS fit's panel]

LD panel .rds (plink_ld_to_rds.R): list(R, variants = data.frame(SNP_ID, CHR, POS, A1, A2[, REF, ALT]), ...)
Fit JSON (same stem as .fit.rds, .json): carries ld_file_declared and/or ld_matrix (the panel the fit read)

src/python/ta_r4/estimands.py:
  region_stat(row): coloc_susie -> pp_h4_max; fallback_abf -> (pp_h4, True); A1_abf_* -> pp_h4; else ValueError
  _both_mask(): both_have_cs is method equality with "coloc_susie"
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Record Carter's W3f decisions (byte-for-byte source file + two DEC entries)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-decisions-2026-11-04.txt, .planning/DECISIONS.md</files>
  <read_first>
    - .planning/DECISIONS.md (last two entries, especially DEC-2026-11-03-run-susie-rss-json-cs-purity-unfreeze: format and the D-28 lift precedent)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md (disposition table)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-CONTEXT.md (D-15, D-28)
  </read_first>
  <action>
    1. Write `$P/W3f-carter-decisions-2026-11-04.txt` with exactly these two lines, byte-for-byte, each ending in a
       single `\n` (Carter's two 2026-11-04 messages, exact text as supplied by the orchestrator; keep the space before
       the period and the spelling "remmeber" in line 2; a decision record, not a sign-off, not `carter-approved` text):
       ```
       fix all as recommended. whats the recommendation for N7?
       go with the recommendation to 'do both' . remmeber we will always choose rigor over speed
       ```
       Write it with `printf '%s\n' '<line 1>' '<line 2>'` (no editor normalisation) and record its `sha256sum`; the sha256
       is computed only from this file as written, never from a normalised paraphrase.
    2. Append two entries at the END of `.planning/DECISIONS.md` (append-only), each citing the file and sha256:
       - `## 2026-11-04 — DEC-2026-11-04-ta-r4-w3f-fix-all: W3f fix-up of the brief-blind review findings before the lock (Carter)`.
         Quote line 1 byte-for-byte. Rule: where an item offered "narrow the text OR widen the code", widen the code. A
         table with one row each for N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N12, N14, T1 giving the target state
         (copy from the must_haves of plans 15.1–15.4) and the implementing plan. N11, N13, N15–N18, T2–T11 were
         fixed in DRAFT text at W4a; T12 rejected; T13 noted.
       - `## 2026-11-04 — DEC-2026-11-04-ta-r4-n7-region-signflip-and-floor: the confirmatory direction test is an exact region-level sign-flip test; n_regions_min 7 (Carter)`.
         Quote line 2 byte-for-byte. State: d_r = b_r − c_r per region on the both_have_cs subset at threshold_primary
         (b = X calls H4 and A3 does not, c = the reverse); T = Σ_r d_r; all 2^k sign assignments over the k regions
         with d_r ≠ 0 enumerated exactly when k ≤ 20, else seeded Monte Carlo with B = bootstrap_B and
         seed = bootstrap_seed, p = (1 + #{|T*| ≥ |T|}) / (B + 1); two-sided p = P(|T*| ≥ |T|); direction = sign(T);
         category names sig_X_gt_A3 / sig_A3_gt_X / ns and alpha 0.025 unchanged; row-level exact McNemar b, c, p
         kept as descriptive output only. `n_regions_min: 7` = distinct regions with ≥ 1 both_have_cs row, checked
         with n_both_min in n_both_ok (failing → NON_INFORMATIVE); counting contributing regions (not discordant ones)
         lets perfect agreement classify as no difference. Justification: the floor is necessary, not sufficient: the
         minimum attainable two-sided p is 2/2^k where k = regions with non-zero d_r; k=6 gives 0.03125 > 0.025, k=7
         gives 0.015625. So 7 contributing regions with one d_r = 0 (k = 6) still cannot reach significance. Placement: inside the `confirmatory:` block,
         so it is bound by `confirmatory_sha256`, which Carter confirms at W4a-T3; the W4a-T3 schema is unchanged.
         A pre-lock measurement suggesting < 7 contributing regions, or < 7 likely discordant regions (k), is a flag
         for Carter; the floor is not lowered.
       The D-28 unfreeze DEC for N1 is NOT written here: "fix all as recommended" is not an explicit unfreeze, and the
       orchestrator has asked Carter for one. Task 2 writes it only from his explicit reply.
    3. Commit the two files (explicit paths): `docs(ta-r4-W3f): Carter's W3f decisions (DEC fix-all, N7)`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && sha256sum .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-decisions-2026-11-04.txt && grep -c "^## 2026-11-04 — DEC-2026-11-04-" .planning/DECISIONS.md && printf '%s\n' "fix all as recommended. whats the recommendation for N7?" "go with the recommendation to 'do both' . remmeber we will always choose rigor over speed" | cmp - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-decisions-2026-11-04.txt</automated>
  </verify>
  <acceptance_criteria>
    - the decisions file is exactly 2 lines and its two lines equal the quoted strings byte-for-byte (`wc -l` = 2; `diff` against a heredoc of the two lines is empty)
    - DECISIONS.md gains exactly 2 headings matching `^## 2026-11-04 — DEC-2026-11-04-` (count printed = 2) and `git diff HEAD~1 -- .planning/DECISIONS.md | grep -c '^-[^-]'` prints 0 (append-only)
    - each DEC cites the decisions file's sha256 (the value printed by sha256sum appears 2 times in the added lines), and `cmp` of the file against `printf '%s\n'` of the two exact lines exits 0
  </acceptance_criteria>
  <done>Carter's decisions are on record, verbatim and append-only, before any code changes.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: N1 — cap after the panel restriction (flag-gated frozen-script edit, R4 argv, re-pin)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-n1-unfreeze-reply.txt, .planning/DECISIONS.md, src/legacy/region_analysis/scripts/run_susie_rss.R, src/python/ta_r4/commands.py, tests/ta_r4/test_cap_after_panel.py, tests/m3/test_source_freeze_pins.py</files>
  <read_first>
    - src/legacy/region_analysis/scripts/run_susie_rss.R lines 655-715 (options), 900-1060 (no_variants exit, cap, LD loop, panel subset)
    - tests/ta_r4/test_frozen_script_armed_e2e.py (fixture pattern for running the frozen script on a tiny panel)
    - tests/m3/test_source_freeze_pins.py lines 55-120 and 170-340 (R_CODE_REF, K-3 containment refs) and commit 52760f08 (the precedent re-pin)
    - tests/m3/test_ld_read_path.py (T2.2 single-line regex on the load_ld_matrix call: do not touch that line)
    - src/python/ta_r4/commands.py, src/python/ta_r4/validate_r4_fits.py (EARLY_EXIT handling)
  </read_first>
  <behavior>
    - Fixture: region whose catalog-joined subset has 40 variants, panel holds 25 of them. SUSIE_MAX_VARIANTS=30.
      Without the flag (or `--cap-after-ld-restriction false`): status too_many_variants, n_variants 40 (unchanged behaviour)
    - Same fixture with `--cap-after-ld-restriction true`: status is not too_many_variants; the .fit.rds has lbf_variable with 25 variant columns (+ "null" if the fit adds it)
    - Same fixture, flag true, SUSIE_MAX_VARIANTS=20: status too_many_variants with n_variants 25, n_variants_pre_ld 40, cap_stage "after_ld_restriction"; the RDS carries the same three fields
    - `--cap-after-ld-restriction maybe` exits non-zero with an error naming the flag (strict true/false, like --ld-authoritative)
    - commands.fit_command for every non-legacy arm on CURRENT_SCRIPT contains `--cap-after-ld-restriction true`; for legacy_any arms and non-CURRENT scripts the flag is absent (import-level test over ARMS)
    - validate_r4_fits classifies the flag-true early exit as early_exit (status-based) without error
  </behavior>
  <action>
    0. BLOCKING PRECONDITION (do this before reading or editing run_susie_rss.R). Carter's explicit N1 unfreeze reply,
       as supplied by the orchestrator: ‹CARTER-REPLY: N1 unfreeze›
       - If the line above still reads `‹CARTER-REPLY: N1 unfreeze›`, or the supplied text is not an explicit
         authorization to edit run_susie_rss.R for N1 (e.g. "N1: unfreeze"), STOP: write nothing, report "N1 blocked:
         no explicit unfreeze from Carter" and end the plan (Task 3 shares commands.py and does not run either).
       - Otherwise save the reply byte-for-byte to `$P/W3f-carter-n1-unfreeze-reply.txt` (`printf '%s\n'`, no
         normalisation), record its sha256, and append to DECISIONS.md
         `## 2026-11-04 — DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze: D-28 lifted once for the N1 cap move in run_susie_rss.R`
         quoting the reply verbatim with the file and sha256. Scope: new option `--cap-after-ld-restriction` (default
         `false`); `true` moves the SUSIE_MAX_VARIANTS check to after the panel restriction and records
         `n_variants_pre_ld` and `cap_stage` in the early-exit JSON and RDS. Default `false` keeps Track B finemap.smk,
         repro arms and the simulation harness on the 53106f8 behaviour (D-15). Nothing else; D-28 is otherwise in
         force. Re-pin `R_CODE_REF` to the N1 code commit (step 6). Commit the two files (explicit paths):
         `docs(ta-r4-W3f): Carter's N1 unfreeze (DEC, D-28 lift)`.
       - Verify: `cmp` of the saved file against the supplied text exits 0; the DEC heading count for this id is 1.
    2. RED: write `tests/ta_r4/test_cap_after_panel.py` (r4_heavy: runs the frozen script with $RSCRIPT) with the
       behaviours above plus the commands.py argv test (not heavy). Run it; paste the failure (optparse rejects the
       unknown flag / argv lacks it) into the SUMMARY.
    3. Implement in run_susie_rss.R, minimal: add
       `make_option("--cap-after-ld-restriction", type = "character", default = "false", help = ...)` next to the
       other ld flags, parsed strictly to TRUE/FALSE (error on any other value). Wrap the existing cap block at :946 in
       `if (!cap_after_ld) { ... }` unchanged. After `subset <- subset[ld_result$subset_idx]` (:1041) add the same
       check under `if (cap_after_ld && nrow(subset) > SUSIE_MAX_VARIANTS)`, writing the same too_many_variants JSON
       and placeholder RDS plus `n_variants_pre_ld` (nrow of the catalog-joined subset before LD loading, saved in a
       variable before the repeat loop), `n_variants` (post-restriction) and `cap_stage = "after_ld_restriction"`,
       then `quit(status = 0)`. Do not modify the single-line load_ld_matrix call. No other behaviour changes.
    4. commands.fit_command: when `script == CURRENT_SCRIPT` and not `_legacy(arm)`, append
       `"--cap-after-ld-restriction", "true"` after `--ld-allele-aware`. Legacy arms unchanged.
    5. GREEN: run the test file. Negative controls, each observed failing then restored (paste outputs):
       NC1 change the new post-restriction check to compare the pre-LD count → the 25-vs-40 fit test fails;
       NC2 drop the flag from fit_command → the argv test fails.
    6. Run `$PY -m pytest tests/m3/test_source_freeze_pins.py -q` → expect RED on the R code pin (paste). Commit the
       N1 code (run_susie_rss.R, commands.py, test_cap_after_panel.py) as
       `fix(ta-r4-W3f): N1 cap after LD restriction (flag-gated, DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze)`.
       Then set `R_CODE_REF` in tests/m3/test_source_freeze_pins.py to the first 7 characters of that commit (update
       exactly that one constant and the trailing "Re-pinned by" comment), re-run the pins file GREEN, and commit
       separately: `test(ta-r4-W3f): re-pin R_CODE_REF to <sha7> (N1 cap move)`. `git fsck --connectivity-only`
       before and after each commit.
    7. Also run tests/m3/test_ld_read_path.py, tests/m3/test_finemap_receipt_early_exit.py,
       tests/ta_r4/test_frozen_script_armed_e2e.py, tests/ta_r4/test_no_silent_identity.py: all outcomes unchanged
       (paste counts). Any changed outcome is STOP-and-report.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_cap_after_panel.py tests/m3/test_source_freeze_pins.py tests/m3/test_ld_read_path.py tests/m3/test_finemap_receipt_early_exit.py tests/ta_r4/test_frozen_script_armed_e2e.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - test_cap_after_panel.py passes; its RED (before step 3) and NC1/NC2 failures are pasted in the SUMMARY
    - `git show --stat` of the N1 code commit lists exactly run_susie_rss.R, commands.py, test_cap_after_panel.py; the re-pin commit lists only tests/m3/test_source_freeze_pins.py
    - test_source_freeze_pins.py is green after the re-pin; test_ld_read_path.py, test_finemap_receipt_early_exit.py, test_frozen_script_armed_e2e.py outcomes are identical to before (counts pasted)
  </acceptance_criteria>
  <done>The cap is applied after the panel restriction for R4 fits only; every other caller is unchanged and the code pin names the authorized commit.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: N2 + N8 — panel-mediated fit-name alignment; method none outputs; commit and LOG</name>
  <files>src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R, src/python/ta_r4/commands.py, src/snakemake/rules/ta_r4_coloc.smk, src/python/ta_r4/estimands.py, tests/ta_r4/test_fit_name_alignment.py, tests/ta_r4/test_coloc_none_states.py, tests/ta_r4/test_coloc_pair_r4.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <read_first>
    - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R (whole file)
    - tests/ta_r4/test_coloc_pair_r4.py, tests/ta_r4/test_fallback_labelled.py, tests/ta_r4/test_qtl_group_runner.py (fixtures that build fits/panels; the current FIT_EARLY_EXIT / COLOC_SUSIE_EMPTY expectations)
    - ta-r4-LOG.md W4a Task 1 entry "Plan vs code" (the 589/589 probe command) and ta-r4-W3-KNOWN-ANSWER-FINDINGS.md item 11
    - data/r4/results/repro_routeC/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.json (which panel field it records)
    - src/python/ta_r4/paths.py (panel_path for production and repro arms), src/snakemake/rules/ta_r4_coloc.smk
    - A1_matched shares one panel across both fits (checker I5): both fits of a pair come from the same arm, region and ancestry, so the single --ld-panel = paths.panel_path(arm, region_safe, ancestry) is the panel for fit_a AND fit_b; FIT_PANEL_MISMATCH is checked against each fit's JSON separately
  </read_first>
  <behavior>
    N2 (map_fit_names(names, ss, panel_variants) -> list(idx, counts) or fail):
    - a fit name equal to a unique ss$name maps directly (current behaviour kept; counted n_direct)
    - otherwise the name must be a unique panel SNP_ID; its CHR:POS must match exactly one ss row whose alleles are allele-compatible with the panel alleles (REF/ALT if present, else A1/A2 as an unordered set): exact, swapped, or the strand complement of either for a non-palindromic SNV; counted n_panel_exact / n_panel_swapped / n_panel_strand
    - unmapped (any of): name absent from both ss and panel; name duplicated in the panel; no ss row at the position; ss row lacking alleles; palindromic A/T or C/G pair matched only through a strand interpretation; allele mismatch; more than one compatible ss row
    - any unmapped name -> error `UNMAPPED_FIT_NAMES: <label>: <n> of <m> fit variant names unmapped (<reason>=<count>, ...); first: <up to 5 names>`; nothing is dropped
    - the panel passed by --ld-panel must equal (realpath) the panel recorded in the fit's JSON (ld_file_declared, else ld_matrix); neither recorded or not equal -> error FIT_PANEL_MISMATCH
    - applied in --mode susie and A1_matched (both fits) and qtl_abf (bridged names, --ld-matrix as the panel)
    - real data (r4_heavy): run_coloc_pair_r4.R --mode susie on repro_routeC SH2B3_12q24 hypertension x stroke (output under data/r4/tmp/w3f/) exits 0 with 0 unmapped; the JSON records the mapping counts
    N8:
    - a fit with no lbf_variable (status no_variants / too_many_variants) -> output written, method "none", none_reason "fit_early_exit:<status_a>|<status_b>" (NA for a side that fitted), PPs null; in --mode susie and A1_matched
    - coloc.susie returning no summary -> method "none", none_reason "coloc_susie_empty", n_snps = shared-variant count; a summary with no finite PP.H4 -> method "none", none_reason "coloc_susie_no_finite_h4"
    - non-converged fits with lbf_variable are unchanged (still enter coloc)
    - estimands.region_stat(method "none") -> (nan, False); estimands.build_rows accepts it; _both_mask is False for it
  </behavior>
  <action>
    1. RED: write tests/ta_r4/test_fit_name_alignment.py (unit cases on tiny in-memory fixtures via $RSCRIPT, plus the
       r4_heavy SH2B3 regression) and tests/ta_r4/test_coloc_none_states.py (R cases for the three none states; a
       Python case for region_stat / build_rows / _both_mask on a method-none doc). Run; paste the failures
       (UNMAPPED_FIT_NAMES 589/589 on SH2B3; FIT_EARLY_EXIT / COLOC_SUSIE_EMPTY errors; region_stat ValueError).
    2. Implement in run_coloc_pair_r4.R: `map_fit_names()` per the behaviour, used by `align_names` (main) and by
       qtl_abf_main in place of `match(b$snps, ss$name)`. Add option `--ld-panel` (required for susie and A1_matched)
       and the FIT_PANEL_MISMATCH check against the fit JSON (path = sub("\\.fit\\.rds$", ".json", fit path)).
       Write the mapping counts per side into the output doc (`name_map_a`, `name_map_b`, named lists of the counts).
       In load_fit, return a sentinel for early-exit fits instead of failing; main writes the method-none doc.
       In coloc_pair_core, return method "none" with `out$none_reason` instead of `fail("COLOC_SUSIE_EMPTY")`, and
       set method "none" / "coloc_susie_no_finite_h4" when no PP.H4 is finite; keep the function's signature and
       return shape (simulate_coloc_r4.R sources it). Add `none_reason` (NA otherwise) to every output doc.
    3. commands.coloc_command: for modes susie and A1_matched add `--ld-panel paths.panel_path(arm, reg, anc)`;
       ta_r4_coloc.smk `_r4_coloc_inputs`: add `"panel": r4paths.panel_path(ARM, reg, anc)` for those modes (and the
       repro arms' own panel_path). estimands.region_stat: `method == "none"` → `(nan, False)`.
    4. Update tests/ta_r4/test_coloc_pair_r4.py where it pinned the old FIT_EARLY_EXIT / COLOC_SUSIE_EMPTY failure
       (the spec changed; replace with the method-none expectation and say so in the SUMMARY). Do not weaken any
       other assertion.
    5. GREEN. Negative controls observed failing then restored (paste): NC1 accept any allele pair at the position
       → the palindrome and mismatch cases fail; NC2 drop the FIT_PANEL_MISMATCH check → its case fails; NC3 make
       region_stat return the PP for method none → the both_have_cs / NaN case fails.
    6. Run tests/ta_r4/test_simulation_harness.py (coloc_pair_core consumer) and test_fallback_labelled.py,
       test_qtl_group_runner.py: outcomes unchanged except deliberate spec updates listed by test id.
    7. §C: $QUICK (record wall time), the r4_heavy files of this plan, pins file. `git fsck`, explicit-path commit
       `fix(ta-r4-W3f): N2 panel-mediated fit-name alignment; N8 method none outputs`, `git fsck`, `git push origin HEAD`.
       Append a LOG entry: DEC ids, commits, RED/GREEN/NC outputs (paths under data/r4/tmp/w3f/), SH2B3 regression
       counts (direct/exact/swapped/strand per side, sum = n fit names), QUICK wall time. Refresh the W3f progress line in the STATE.md RESUME block (§C). Commit the LOG and STATE.md (explicit paths), push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_fit_name_alignment.py tests/ta_r4/test_coloc_none_states.py tests/ta_r4/test_coloc_pair_r4.py tests/ta_r4/test_simulation_harness.py tests/ta_r4/test_fallback_labelled.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - all listed tests pass; RED outputs and NC1–NC3 failures are pasted in the SUMMARY
    - SH2B3 regression: rc 0, 0 unmapped on both sides; the per-side counts sum to the fit's variant count (589 for hypertension, 622 for stroke, per the W4a probe) — reconciled in the LOG
    - a method-none JSON from each of the three states is parsed by estimands.build_rows without error and has both_have_cs False in paired_frame (test assertion)
    - `git log origin/m3-W2-aou-deltas..HEAD` is empty after the push
  </acceptance_criteria>
  <done>EUR pairs no longer refuse on rsid vs chr:pos names, and every early-exit or empty-summary state is a labelled, reportable row.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| frozen producer → every caller | an edit to run_susie_rss.R can change Track B and reproduction outputs |
| fit names → coloc variant keys | a wrong mapping silently pairs the wrong variants |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W3f1-01 | Tampering | run_susie_rss.R cap move | mitigate | flag default false; pre-existing frozen-script tests unchanged; R_CODE_REF re-pinned in a separate commit under a DEC |
| T-r4-W3f1-02 | Tampering | map_fit_names | mitigate | allele check with palindrome refusal; FIT_PANEL_MISMATCH; hard error on any unmapped name; negative controls |
| T-r4-W3f1-03 | Repudiation | Carter's decisions | mitigate | verbatim decisions file with sha256 cited in append-only DEC entries |
</threat_model>

<verification>
N1, N2 and N8 behaviours pass with observed RED and negative controls; the frozen-script pin and all pre-existing
frozen-script tests are green; the SH2B3 regression maps every fit name.
</verification>

<success_criteria>
The two production blockers from the W4a checkpoint (cap before restriction; unmapped fit names) are fixed in the
producer and consumer, and the three crash states are reportable rows.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-producer-cap-fit-names-early-exit-SUMMARY.md`
</output>
