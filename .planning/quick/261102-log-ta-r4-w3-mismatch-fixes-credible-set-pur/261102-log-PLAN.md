---
phase: quick-261102-log
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/quick/261102-log-ta-r4-w3-mismatch-fixes-credible-set-pur/carter-d28-reply.txt
  - src/legacy/region_analysis/scripts/run_susie_rss.R            # Task 3, ONLY if Carter authorizes the D-28 unfreeze
  - tests/ta_r4/test_json_cs_equals_fit_sets.py                   # Task 3, ditto
  - tests/m3/test_source_freeze_pins.py                           # Task 3, R_CODE_REF bump only
  - .planning/DECISIONS.md
  - .planning/STATE.md
autonomous: false
requirements: [REQ-SUSIE-RSS-POLICY]
must_haves:
  truths:
    - "TRACK-A-FROZEN-NUMBERS.md ends with a dated 2026-11-02 ERRATA section; every original line is unchanged (git diff shows additions only)"
    - "Each erratum names the affected line by number AND a quote, and cites the source path for the correcting fact"
    - "FINDINGS §4 names the 4 fits (asthma/bmi/hypertension/t2d .EUR.FTO_16q12) and the cause (identity-placeholder LD in the April fire)"
    - "FINDINGS §8 says R1 read the 2026-04-30 V4 fits, its mechanism sentence was not measured, and 3 FTO pairs reached coloc.susie"
    - "Carter's verbatim D-28 decision is on disk before any edit to run_susie_rss.R"
    - "If unfreeze authorized: JSON credible_sets count == length(readRDS(fit)$sets$cs) on a fixture with an impure set; the test was observed RED before the fix and its negative control observed RED after"
    - "If unfreeze authorized: .fit.rds is byte-identical before vs after the fix (fixture + 1 real fit, md5)"
    - "data/r4/legacy_code/run_susie_rss_3dd76df.R (Route L) and run_susie_rss_02c4404.R are untouched (sha256 = legacy_code_sha256.tsv)"
  artifacts:
    - path: ".planning/amendments/TRACK-A-FROZEN-NUMBERS.md"
      provides: "ERRATA (2026-11-02) section, appended"
      contains: "ERRATA (2026-11-02)"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md"
      provides: "§4/§7/§8 updated with measured causes"
    - path: "tests/ta_r4/test_json_cs_equals_fit_sets.py"
      provides: "RED-first producer test (Task 3, authorized branch only)"
  key_links:
    - from: "run_susie_rss.R JSON credible_sets"
      to: "fit$sets$cs read by run_coloc_susie.R"
      via: "susie_get_cs(fit, Xcorr = <LD the fit used>, coverage = <fit coverage>, min_abs_corr = MIN_ABS_CORR_DEFAULT)"
    - from: "tests/m3/test_source_freeze_pins.py R_CODE_REF"
      to: "the commit that lands the fix"
      via: "re-pin protocol in tests/m3/source_freeze.py:28-38 (one constant, nothing else)"
---

<objective>
Act on Carter's W3b-T3 instruction "lets fix these mismatches" (signoffs/W3b-T3.yaml, raw_sha256 e8800b8e…).

1. Record the measured causes as dated errata in the frozen-numbers file and in the W3 FINDINGS (docs; autonomous).
2. Get Carter's explicit decision on unfreezing `run_susie_rss.R`. ⚠ The brief asks for a producer edit to this file, but
   **D-28 (ta-r4-CONTEXT.md:148, LOCKED) and PLAN-INDEX §B.6 say it is "never edited"**. "Fix these mismatches" does not
   name the file or D-28. A relayed brief cannot lift a locked decision, so Task 2 is a `checkpoint:human-action`
   (the only checkpoint type that stops under auto mode, §D).
3. If authorized, land the producer fix TDD RED-first with a negative control, prove `.fit.rds` is unaffected, re-pin
   `R_CODE_REF`, run the wave-close tiers and push. If not authorized, record the decision and make no code edit.

Constraints carried into every task: §B.10 (nothing re-run or tuned toward a frozen value), §B.1 explicit-path `git add`
(many unrelated untracked files exist: never `-A` / `.`), §B.13 keep edits short, `Co-Authored-By: Claude Opus 5.5
<noreply@anthropic.com>` trailer, `git push` after each commit (origin is SSH; branch `m3-W2-aou-deltas`).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
$P = .planning/phases/ta-r4-head-to-head-reanalysis-and-submission ; $MAN = $P/manifests
PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11
RSCRIPT=/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript   (the ta_r4 tests' R; see tests/ta_r4/test_frozen_script_armed_e2e.py:28)
QUICK="$PY -m pytest tests/ta_r4 -x -q -m 'not r4_heavy'" ; HEAVY="$PY -m pytest tests/ta_r4 -q -m r4_heavy -rs"
FULL="$PY -m pytest tests/ta_r4 tests/m3 tests/phase1 tests/phase2 -q"   (last: 1888 / 1838 / 50 / 0, full_W3b.xml)

@.planning/STATE.md
@$P/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md
@.planning/debug/ta-r4-w3-status-split-and-r1-fto.md
@$P/ta-r4-PLAN-INDEX.md   (§B rules, §C wave close)

<interfaces>
run_susie_rss.R (current, R_CODE_REF bf04199):
- :30-67 run_susie_with_ladder(z, R, policy, n): fit1 R/max1, fit2 R/max2, fit3 regularize_ld(R)/max2; susie_rss(..., coverage = policy$coverage)
- :1113-1123 R <- diag(n) when ld_result$R is NULL, else symmetrized panel R with diag 1
- :1127-1133 ladder_policy$coverage = opt$`credible-set` %||% COVERAGE
- :1143-1157 ladder exhausted -> refit on diag(nrow(subset)); NOTE `R` is NOT reassigned here (still the panel R)
- :1158 `cs <- susie_get_cs(fit)`   <- THE DEFECT: no Xcorr => no purity filter; feeds JSON credible_sets (:1160-1166)
- :1238-1266 annotate_susie(fit, snp_names, R) then saveRDS(fit)  <- must NOT change (fit.rds byte-identical)
- :1320-1338 min_abs_corr sweep + n_cs_default use susie_get_cs(fit, Xcorr = R, coverage = COVERAGE, min_abs_corr = ...)
- constants :748 COVERAGE, :752 MIN_ABS_CORR_DEFAULT (0.5)
fit$sets in the .fit.rds = susieR 0.14.2 susie_rss's own purity-filtered sets (min_abs_corr 0.5), annotated by coloc:::annotate_susie.
Measured (brief): on 66/66 reproduced fits with sets, rds set count == JSON sweep n_CS at 0.5; 29 differ from JSON credible_sets
($MAN/fit_cs_json_vs_rds.tsv columns: trait ancestry region_safe status n_cs_json n_cs_rds_sets eq).

Pins on run_susie_rss.R:
- tests/m3/test_source_freeze_pins.py:71 `R_CODE_REF = "bf04199"` — the ONLY place the R code pin is spelled; imported by
  test_finemap_receipt_early_exit.py:79 and test_qtl_coloc_allele_join.py:129. Re-pin protocol: tests/m3/source_freeze.py:28-38
  (update exactly R_CODE_REF to the landing commit; NEVER bump DIFFERENTIAL SUBSTRATE / HISTORICAL NARRATIVE constants such as
  K3_PRE_FIX_REF or the pin in test_variant_catalog_fallback_legacy_semantics.py:79).
- $MAN/legacy_code_sha256.tsv pins the EXTRACTED copies (3dd76df, 02c4404) under data/r4/legacy_code/ — not the live file; untouched.
- src/python/ta_r4/arms.py:4 CURRENT_SCRIPT (Route C) = live file; :5 LEGACY_SCRIPT (Route L) = data/r4/legacy_code/run_susie_rss_3dd76df.R.
- src/python/ta_r4/r4_lock_gate.py:32 lists the live file as a LOCKED path; no lock record exists yet (W4b), so editing now is pre-lock.

k2d cs_sizes writer: IDENTITY-LD-K2D-FIT-SUMMARY.tsv was produced by quick-260425-ieh (commit ec86832e), whose PLAN :161 specifies
"len(cs) for each cs in JSON.credible_sets" (iterating a dict gives the key "CS<i>"). The current
src/legacy/region_analysis/scripts/summarize_finemap_results.py:17-19 uses `len(entries)` on `.items()` (emits "CS<i>:<size>").
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: ERRATA in TRACK-A-FROZEN-NUMBERS.md + FINDINGS §4/§7/§8 + LOG (docs only)</name>
  <files>.planning/amendments/TRACK-A-FROZEN-NUMBERS.md, $P/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md, $P/ta-r4-LOG.md</files>
  <action>
Read each source before quoting it. Re-locate every frozen-file line by grep of a unique quote (line numbers in the brief are
approximate: :26, :72, :180-188, :222, :357, :361). Cite each erratum as "`:<n>` "<short quote>"".

(1) cs_sizes writer check (feeds erratum E1). Run and paste: `grep -rn "IDENTITY-LD-K2D-FIT-SUMMARY" bin src` (expect no writer
in code), `git show ec86832e --stat`, and the ieh PLAN :161 spec line. Then run the CURRENT summarize_finemap_results.py's
`summarize_file` on one reproduced non-empty k2d JSON (data/r4/results/repro_k2d_routeC/fine_mapping/susie/, pick one with
n_CS ≥ 2) via `$PY -c` and paste `credible_set_sizes` next to `len(v)` per set from the JSON. If they agree, the verdict is
"not present in current code" with that evidence; if the current code reproduces `3;3;…`, STOP and add a TDD fix as a
Task 3 sub-step (report it; do not fix inline here).

(2) Append to the END of TRACK-A-FROZEN-NUMBERS.md (do not edit any existing line; `git diff` must be additions only):
`## ERRATA (2026-11-02) — ta-r4 W3 known-answer findings`, a one-line preface (frozen lines are kept as written; these entries
correct them; source: ta-r4 W3 FINDINGS + debug file), then numbered entries E1–E7, each 1–3 lines, each with source path(s):
- E1 k2d `cs_sizes` (IDENTITY-LD-K2D-FIT-SUMMARY.tsv, cited at :26/:20 area) = length of the label `CS<i>`, not set size;
  95/95 rows; do not cite for set sizes. Sources: FINDINGS §3, W3a SUMMARY:146-149, item (1) evidence.
- E2 `:72` "sole "ok" SH2B3 EUR fit" contradicts `:222` and the reproduction: t2d.EUR.SH2B3_12q24 is also ok (JSON n_CS 9).
  Source: `$MAN/known_answer_W3a.tsv`, FINDINGS §4.
- E3 `:357` / `:361` misattribute R2: R2 coloc = run_coloc_susie.R at c0f02b6, fits = run_susie_rss.R at 02c4404 via
  `bin/fire_canonical_susie_pairs_W2_strategy3.sh`; reproduced L15 `.fit.rds` md5 903782e2… / 3dc6fe83… / 4c539b5a…; coloc
  output byte-identical 9/9. The md5s at :361 are the 2026-04-30 V4 rebuild (c8ee71a0); b3395d9 is a V4 dispatch record.
  Sources: FINDINGS §5, `$MAN/fits_repro_sh2b3_sha256.tsv`, ta-r4-LOG.md 2026-10-29 W3b.
- E4 `:180-188` 48 ok / 18 non_converged: the April fire fitted all 5 FTO_16q12 EUR traits on the identity-placeholder LD RDS
  (ld_status variants_exceed_threshold, ld_overlap_fraction 0). On the real 1000G EUR panel asthma/bmi/hypertension/t2d
  .EUR.FTO_16q12 are non_converged → 44 / 22 (24 / 6 unchanged; non-empty 51 unchanged). Evidence: debug file (1e4b071e
  figure snapshot, 5-scalar reconciliation), `src/R/figures/fig1b_locus_panels.R:33-35`. Why the canonical FTO RDS was still a
  placeholder at fire time is not measured.
- E5 "51 / 96 non-empty" (:15, :182 area) counts the fit JSON `credible_sets`, which carried no purity filter; the sets
  coloc.susie reads (`.fit.rds` `$sets$cs`) are non-empty for 25/96. Source: `$MAN/fit_cs_json_vs_rds.tsv`, FINDINGS §4.
- E6 R1 28/28 (:155/:171-172 area, and the mechanism sentence in
  `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-trait-pair-coloc-refire-SUMMARY.md:25/:66`): the
  "n_cs_a=0 OR n_cs_b=0" mechanism was not measured. R1 (2026-05-06) read the 2026-04-30 V4 fits; its committed
  `d9707dfa:results/multitrait/coloc_summary.tsv` has non-null PP.H0 for 3 FTO EUR pairs (asthma_vs_bmi, asthma_vs_t2d,
  bmi_vs_t2d), the no_posterior shape, so they reached coloc.susie. The measured R1 fact is non-empty PP.H4 0/28.
  Source: debug file Evidence/Resolution #6.
- E7 (open item, NOT fixed here) latent alignment defect: fits named by LD-panel rsid (7d54183b override) vs sumstats
  `SNP_ID` chr:pos → with R.utils present, run_coloc_susie.R's chr:pos rewrite maps 6/1833 (htn) and 8/2372 (t2d) and the
  intersect is 0. Source: debug file, LSF 481827 replay.
Re-measure any count you write with a pasted command (e.g. `awk` over fit_cs_json_vs_rds.tsv: eq/differ/no-sets and 51 − 26 = 25).

(3) FINDINGS edits (keep the existing table numbers; edit prose only; every new number cites its source):
- §4 first bullet: replace "the 4 cannot be named" with the 4 fit ids + cause (E4 wording) and the reconciliation
  (44+4=48, 22−4=18, non-empty 51 unchanged; ld_loaded 40−5=35, below-0.5 30+3=33, FTO min ld_of 0). Mark the env-drift
  caveat as no longer needed to explain the 4 (debug file "Eliminated").
- §7 item 3: append "the producer defect is item 10". Item 4: now named + caused (E4). Item 9: rewrite per E6 (R1 used V4 fits;
  mechanism unmeasured; 3 FTO pairs reached coloc.susie; measured fact PP.H4 0/28).
- §7 new item 10: run_susie_rss.R:1158 computes JSON `credible_sets` with `susie_get_cs(fit)` (no Xcorr, no purity filter)
  while `fit$sets` is purity-filtered at min_abs_corr 0.5; status line "fix pending Carter's D-28 decision (quick-261102-log
  Task 2)". Task 3 replaces the status line.
- §7 new item 11: the latent alignment defect (E7), open, not fixed.
- §8: after the "cause … was not measured" bullet, add the measured cause (R1 read V4 fits; V4 FTO EUR n_cs bmi 7 / htn 0 /
  t2d 2 vs reproduced 3/5/7, from logs/ta_r3_W3_r2_parity/r2_parity_dispatch.log via the debug file; 3 htn pairs no_signal;
  3 pairs no_posterior per d9707dfa) and change "The cause of the difference was not measured" to past-tense historical
  ("was not measured at W3b; measured 2026-11-02, see debug file").

(4) Append `## 2026-11-02 — quick-261102-log Task 1: W3 errata + FINDINGS causes` to $P/ta-r4-LOG.md (what changed, the
counts with reconciliation, commit sha after commit). Keep it short (§B.13).

(5) `git fsck --connectivity-only | tail -3`; `git add` the three explicit paths; commit `docs(ta-r4-W3): errata for frozen
numbers + measured W3 mismatch causes`; fsck again; `git push`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && test "$(git diff HEAD~1 -- .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | grep -c '^-[^-]')" = "0" && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import pathlib,sys; t=pathlib.Path('.planning/amendments/TRACK-A-FROZEN-NUMBERS.md').read_text(); i=t.index('## ERRATA (2026-11-02)'); s=t[i:]; sys.exit(0 if all(f'E{k}' in s for k in range(1,8)) else 1)" && git status --porcelain -- .planning/amendments/TRACK-A-FROZEN-NUMBERS.md .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md | wc -l | grep -qx 0</automated>
  </verify>
  <done>Errata E1–E7 appended (zero deleted lines in the frozen file), each with a line quote and source path; FINDINGS §4/§7(3,4,9,10,11)/§8 updated with sources; cs_sizes verdict recorded with pasted evidence; LOG entry; committed by explicit paths and pushed.</done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 2: Carter decides the D-28 unfreeze of run_susie_rss.R</name>
  <what-built>Task 1 errata and FINDINGS are committed. No code has been changed.</what-built>
  <action>Present this to Carter verbatim-ready, then WAIT. Do not edit run_susie_rss.R before a valid reply is saved.

D-28 (ta-r4-CONTEXT.md:148, locked) and PLAN-INDEX §B.6 say `run_susie_rss.R` is never edited. Your "lets fix these mismatches"
does not name the file. The producer fix needs it edited, so I need an explicit decision.

Proposed change (about 6 code lines, before the ta-r4 lock):
- At :1158, compute the JSON credible sets as `susie_get_cs(fit, Xcorr = R_cs, coverage = ladder_policy$coverage,
  min_abs_corr = MIN_ABS_CORR_DEFAULT)`, where `R_cs` is the LD the fit used (`R`; or `diag(nrow(subset))` in the
  ladder-exhausted identity branch at :1143-1157, where `R` is currently not reassigned).
- Use the same `R_cs` in the min_abs_corr sweep and `n_cs_default` (:1320-1338). This only changes the ladder-exhausted branch.
- Not changed: the fit, `annotate_susie(…, R)` and `saveRDS`, so `.fit.rds` stays byte-identical (proved by md5).
  Route L (the 3dd76df copy) and the 02c4404 copy are not touched. `R_CODE_REF` is re-pinned to the landing commit.

Effect: from now on JSON `credible_sets` equals the sets coloc.susie reads, for Route C and production (W5a). Route C JSON no
longer equals Route L JSON on fits with impure sets (29 of the W3a fits). W3a/W3b outputs are not re-run (§B.10).

Alternative (keep D-28): no code edit. R4 defines a credible set as `.fit.rds` `$sets$cs` downstream (FINDINGS §7 item 3).
JSON `credible_sets` stays unfiltered and is never cited as a CS count.

Reply format (first line required):
  carter-approved YYYY-MM-DD
  d28: unfreeze      (or)      d28: keep
  </action>
  <how-to-verify>Carter's reply is saved byte-for-byte to `.planning/quick/261102-log-ta-r4-w3-mismatch-fixes-credible-set-pur/carter-d28-reply.txt` and its sha256 printed. Valid only if line 1 matches `^carter-approved 20\d\d-\d\d-\d\d$` and a `d28:` line is exactly `unfreeze` or `keep`. A bare "approved", an auto-mode response, a summary or paraphrase = WAIT: re-present and write nothing (§B.15). The executor never authors this text.</how-to-verify>
  <files>.planning/quick/261102-log-ta-r4-w3-mismatch-fixes-credible-set-pur/carter-d28-reply.txt</files>
  <verify><automated>head -1 .planning/quick/261102-log-ta-r4-w3-mismatch-fixes-credible-set-pur/carter-d28-reply.txt | grep -Eqx 'carter-approved 20[0-9]{2}-[0-9]{2}-[0-9]{2}' && grep -Eqx 'd28: (unfreeze|keep)' .planning/quick/261102-log-ta-r4-w3-mismatch-fixes-credible-set-pur/carter-d28-reply.txt</automated></verify>
  <done>Carter's verbatim reply saved with sha256; decision is unfreeze or keep.</done>
  <resume-signal>Carter's verbatim reply: "carter-approved YYYY-MM-DD" + "d28: unfreeze" or "d28: keep"</resume-signal>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Producer fix RED-first (if d28: unfreeze) or record keep-freeze; re-pin; wave close; push</name>
  <files>src/legacy/region_analysis/scripts/run_susie_rss.R, tests/ta_r4/test_json_cs_equals_fit_sets.py, tests/m3/test_source_freeze_pins.py, .planning/DECISIONS.md, $P/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md, $P/ta-r4-LOG.md, .planning/STATE.md, .planning/quick/261102-log-ta-r4-w3-mismatch-fixes-credible-set-pur/carter-d28-reply.txt</files>
  <behavior>
    - T1 (RED before, GREEN after): running the working-tree run_susie_rss.R on a fixture whose unfiltered CS list contains an impure set, len(JSON credible_sets) == length(readRDS(fit.rds)$sets$cs), and the variant membership of each JSON set equals the corresponding fit$sets$cs names.
    - T2 precondition guard (must hold in BOTH states): on that fixture, length(susie_get_cs(fit)$cs) > length(fit$sets$cs), i.e. the fixture really contains an impure set. Without this, T1 could be green over nothing.
    - T3: .fit.rds md5 from the pre-fix script (`git show <PRE_FIX_SHA>:<path>`, a DIFFERENTIAL SUBSTRATE constant, never re-pinned) equals the md5 from the working-tree script on the same fixture.
  </behavior>
  <action>
First, `signoff`-style check by hand: read carter-d28-reply.txt and confirm it is valid per Task 2. Print its sha256.

BRANCH keep (`d28: keep`): no code edit. Add DEC-2026-11-02-run-susie-rss-json-cs-keep-freeze to .planning/DECISIONS.md
(the reply quoted, sha256, the consumer-side CS definition). Set FINDINGS §7 item 10 status to "not fixed in code by Carter's
decision (DEC…); CS counts use `.fit.rds` `$sets$cs`". LOG + STATE, commit by explicit paths, push. Then run QUICK + pins only.
Stop.

BRANCH unfreeze (`d28: unfreeze`):
(a) Pin inventory (paste output): `git grep -n "run_susie_rss" -- tests bin config src/python | grep -iE "sha|md5|blob|diff|REF|pin"`,
`git grep -n "bf04199" -- tests`, and sha256 of data/r4/legacy_code/run_susie_rss_{3dd76df,02c4404}.R vs $MAN/legacy_code_sha256.tsv
(must match before and after). Classify each hit: CODE pin to re-pin (expected: only R_CODE_REF), DIFFERENTIAL/HISTORICAL
(never re-pin), or extracted-copy pin (untouched). If any other live-file pin exists, pin the behaviour per memory rule, not a
new fixed SHA; report it.

(b) RED. Write tests/ta_r4/test_json_cs_equals_fit_sets.py (mark `r4_heavy` if > ~20 s; reuse the fixture/run helpers pattern
of tests/ta_r4/test_frozen_script_armed_e2e.py: RSCRIPT path, `_env`, `build_fixture`, the r4 command from ta_r4.commands, or a
direct Rscript call with a fixture regions CSV/sumstats/LD RDS). The fixture must yield an impure unfiltered set; a reliable
construction is LD mismatch: z simulated from one LD matrix R0 (two moderately-correlated blocks with 2 causal variants),
then the script given a different panel R (e.g. block signs flipped or correlations shrunk) so susie_rss spreads an effect over
weakly-correlated variants. Find a deterministic seed/config with a throwaway scratch R probe (scratchpad dir) checking T2;
commit only the final fixture builder. If no synthetic fixture shows T2 after reasonable effort, use the live substrate instead:
re-run one ok fit with eq=false from $MAN/fit_cs_json_vs_rds.tsv (inputs as in its repro_routeC Snakemake command) into a
tmp_path, as an `r4_heavy` test. Run the test: it must FAIL on T1 with T2 passing. Paste the failing output.

(c) GREEN. Edit only the lines named in Task 2: add `R_cs <- R` after :1123 block (before the ladder), `R_cs <- diag(nrow(subset))`
inside the ladder-exhausted branch (do NOT reassign `R`: annotate_susie at :1255 reads it and the fit.rds must not change),
change :1158 to `cs <- susie_get_cs(fit, Xcorr = R_cs, coverage = ladder_policy$coverage, min_abs_corr = MIN_ABS_CORR_DEFAULT)`,
and swap `Xcorr = R` for `Xcorr = R_cs` at the sweep and `n_cs_default`. No comment essays (§B.13). Test GREEN; paste.

(d) Negative control (§B.2): temporarily revert :1158 to `susie_get_cs(fit)` (keep a sha256 of the fixed file), re-run → T1
must FAIL; restore and confirm the file's sha256 equals the fixed one. Clear `__pycache__` is irrelevant for R; paste outputs.

(e) fit.rds unaffected: T3 green on the fixture. Plus one real fit on LSF (serial queue via config/bsub_wrapper.sh; never
`short`): re-run 1 ok eq=false fit (and, if cheap, 1 non_converged fit) with the fixed script into
data/r4/tmp/261102-log/ and compare `.fit.rds` md5 to the repro_routeC copy; also confirm the new JSON `credible_sets` count
equals that fit's `n_cs_rds_sets`. This is a fit-identity check, not a re-run toward a frozen value (§B.10); write nothing
into data/r4/results/.

(f) Commit F (explicit paths: script + test): `fix(ta-r4): JSON credible_sets purity-filtered like fit$sets (D-28 unfreeze,
Carter 2026-11-02)`. Then re-pin: change ONLY `R_CODE_REF` in tests/m3/test_source_freeze_pins.py to F's short SHA; run
`$PY -m pytest tests/m3/test_source_freeze_pins.py tests/m3/test_finemap_receipt_early_exit.py
tests/m3/test_qtl_coloc_allele_join.py -q` (green), and observe the pin can fail: set R_CODE_REF to the parent of F → RED →
restore. Add DEC-2026-11-02-run-susie-rss-json-cs-purity-unfreeze to DECISIONS.md (reply quote + sha256, scope, F). Commit
`test(ta-r4): re-pin R_CODE_REF to <F>` with the pins file + DECISIONS.md.

(g) Wave close per PLAN-INDEX §C: `time $QUICK`, `$HEAVY`, pins, then `$FULL` on LSF (≥ 40 min; standard queue ≥ 8 slots or
long) with `--junitxml data/r4/tmp/261102-log/full_261102.xml`. Compare by test id to full_W3b.xml: removed 0, tests/m3
outcome changes 0, only additions in tests/ta_r4. Any changed pre-existing outcome = STOP and report (do not edit the test).
Restore tests/m3/sparse_parent_benchmark.tsv after the full run (`git checkout -- tests/m3/sparse_parent_benchmark.tsv`) and
confirm `git status --porcelain` for it is empty. Confirm legacy_code sha256 unchanged.

(h) FINDINGS §7 item 10 status → "fixed in F (DEC…); W3a/W3b outputs not re-run; Route C JSON now differs from Route L JSON
on impure-set fits; state in the W4a amendment". LOG entry (RED/NC/GREEN outputs, md5s, suite counts with reconciliation,
commit SHAs, push result). Refresh the ★ RESUME HERE ★ Track A block in STATE.md. Commit by explicit paths; fsck before/after;
`git push`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/m3/test_source_freeze_pins.py -q && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_json_cs_equals_fit_sets.py -q -rs && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -x -q -m 'not r4_heavy' && (cd data/r4/legacy_code && sha256sum run_susie_rss_3dd76df.R run_susie_rss_02c4404.R) && git status --porcelain -- tests/m3/sparse_parent_benchmark.tsv | wc -l | grep -qx 0</automated>
  </verify>
  <done>keep: DEC + FINDINGS/LOG/STATE recorded, no code change, pushed. unfreeze: T1 observed RED then GREEN, NC observed RED, T2 holds in both states, fit.rds md5 identical (fixture + ≥1 real fit), only R_CODE_REF re-pinned and shown able to fail, extracted legacy copies unchanged, QUICK/HEAVY/pins green, FULL = full_W3b ids + additions only with 0 tests/m3 outcome changes, benchmark TSV restored, FINDINGS item 10 + DEC + LOG + STATE written, all commits pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| relayed brief → frozen code | an orchestrator brief asks for an edit a locked decision (D-28) forbids |
| frozen record → public amendment | errata feed W4a; a wrong erratum propagates into public text |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-261102-01 | E | run_susie_rss.R D-28 freeze | mitigate | Task 2 human-action checkpoint; edit only after a valid verbatim `d28: unfreeze` reply is saved with sha256 |
| T-261102-02 | T | TRACK-A-FROZEN-NUMBERS.md | mitigate | append-only; Task 1 verify fails on any deleted line |
| T-261102-03 | T | .fit.rds produced by the fixed script | mitigate | md5 equality pre/post on fixture (T3) and ≥1 real LSF fit |
| T-261102-04 | R | freeze pin | mitigate | only R_CODE_REF bumped, to the landing SHA, and shown able to fail; differential substrates untouched |
| T-261102-05 | I | public framing | accept | internal records only; no OSF/journal action in this task |
</threat_model>

<verification>
- Frozen file: additions only; E1–E7 each cite a line quote and a source path.
- FINDINGS §4/§7/§8: every new number has a source.
- Carter reply on disk (sha256) before any script edit.
- unfreeze branch: RED/NC/GREEN outputs and md5 comparisons pasted in the SUMMARY; FULL compared by id to full_W3b.xml.
</verification>

<success_criteria>
The W3 mismatches carry measured causes in the record (errata + FINDINGS), the producer defect is either fixed with RED-first
proof and an unchanged fit object, or explicitly kept frozen by Carter's decision, and every commit is pushed.
</success_criteria>

<output>
After completion, create `.planning/quick/261102-log-ta-r4-w3-mismatch-fixes-credible-set-pur/261102-log-SUMMARY.md`
</output>
