---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7h2
slug: W3f-proxy-asthma-refit
type: execute
wave: 15.7h2
depends_on: ["ta-r4-W3f-null-window-reselection"]
gap_closure: true
files_modified:
  - .planning/DECISIONS.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7h2-mem-and-k2d-mapping-reply-2026-11-21.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7h2-drop-asthma-reply-2026-11-22.txt
  - src/python/ta_r4/measure_fit_eligibility.py
  - tests/ta_r4/test_proxy_exact_purity.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/proxy_asthma_pilot_fits_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_region_contribution_proxy.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_157h2_build_check.tsv
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/HANDOFF.json
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-proxy-asthma-refit-SUMMARY.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-NEGATIVE-CONTROLS

must_haves:
  truths:
    - "Gates: Q-PROXY prints \"Add to 15.7j (Recommended)\", Q-PROXYA prints \"B: Run the 20 asthma fits\", Q-PROXYB prints \"A: Run as planned (Recommended)\", and Q-NREG matches the free text \"yes, A and add D to 15.7j and keep 7\", each with its <question> text and sha256; Q-PURITY's file (committed in d2b01ee1) passes `git ls-files --error-unmatch`, `git diff --quiet HEAD --` on it, sha256 bf5185dc…8f614a6, and `[ \"$(tail -n 1 f)\" = \"Carter reply (verbatim, selected option): A: use the scored matrix (Recommended)\" ]`; otherwise nothing is edited or run. Right after the Q-PURITY gate, commit 1b adds DEC-2026-11-21-ta-r4-proxy-exact-purity-scored-matrix to DECISIONS.md: it quotes the reply file (cat + cmp), records the false premise (the pre-revision must-have text \"so only n_purity differs from fit time\" and its single-matrix identity check) and the candidate rule of the exact-purity must-have. Q-MEMK2D's file (W3f-carter-15-7h2-mem-and-k2d-mapping-reply-2026-11-21.txt, untracked until commit 1c) has sha256 c2783c9b…1030c, line 3 byte-equal to \"Carter reply (verbatim, selected option): Raise to 56G (Recommended)\" and line 7 byte-equal to \"Carter reply (verbatim, selected option): A: skip mapping (Recommended)\"; otherwise nothing more is edited or run. Right after the Q-MEMK2D gate, commit 1c (DECISIONS.md + that file) adds DEC-2026-11-21-ta-r4-proxy-k2d-identity-and-56g: it quotes the file (cat + cmp) and records the k2d memory gate and the identity-panel mapping rule. Q-DROPASTHMA's file (W3f-carter-15-7h2-drop-asthma-reply-2026-11-22.txt, untracked until commit 1d) has sha256 072f5279…b402 and `[ \"$(tail -n 1 f)\" = \"Carter reply (verbatim): yes, drop asthma and check the production catalog\" ]`; otherwise nothing more is edited or run. Right after the Q-DROPASTHMA gate, commit 1d (DECISIONS.md + that file) adds DEC-2026-11-22-ta-r4-proxy-drop-asthma-build-mix: it quotes the file (cat + cmp) and says it narrows Q-PROXYA B (\"Run the 20 asthma fits\"): the fits ran, but their use in the proxy is withdrawn. (Q-PROXY named 15.7j; Q-PROXYA moved the work here, before 15.7i, so the F15 recount sees the new fits)"
    - "Inputs are measured and pinned before any fit: the corrected asthma EUR file data/r4/sumstats/asthma.EUR.grch37_lifted_strand.tsv.bgz (sha256 49edfc54…0c7e2b, manifests/sumstats_r4_sha256.tsv), the legacy-route catalog of each region (paths.catalog_path('legacy', region)), the repro panels (legacy_repro/EUR, k2d_identity/EUR, via the arms' panel manifests), the script and policy the repro arms use (CURRENT_SCRIPT, POLICY_REPRO); every sha256 is checked against its manifest or recorded, in $Q/proxy_asthma_inputs.tsv"
    - "Exactly 20 pre-lock pilot commands are run: asthma × EUR × the 10 confirmatory regions × {repro_routeC, repro_k2d_routeC}, with each arm's own commands.fit_command argv except --sumstats (the corrected file) and --output (data/r4/measure_asthma_fix/fits/proxy_asthma_<arm>/asthma.EUR.<region>.json), so nothing is written under data/r4/results; no receipt, validator, colocalization or production rule runs; the 40 JSON + RDS are sha256-manifested in manifests/proxy_asthma_pilot_fits_sha256.tsv. Measured by the split (Slurm 2025948): 12 fit (APOE_19q13, APOL1_22q12, CXADR_F2RL1_6p21, FTO_16q12, MC4R_18q21, SH2B3_12q24 × both arms) and 8 exit early as too_many_variants (9p21_CDKN2A, BMI_5q13_3, PYHIN1_1q23, SLC2A9_urate × both arms). The 12 fits (24 files) are the pilot fits 15.7i counts and discloses; the 8 early-exit outputs (16 files) carry no fit. All 40 files are kept and manifested as pre-lock pilot fits, never a proxy or lock input (Q-DROPASTHMA): the legacy catalog carries the superseded GRCh38 asthma positions, so a corrected-asthma fit through the legacy route mixes builds"
    - "The fits run under Slurm: sbatch -p compute -A clintonlab_cpu -q normal --constraint=cascadelake repro_routeC --mem=48G -t 01:00:00 and repro_k2d_routeC --mem=56G (Q-MEMK2D 1) -t 02:00:00 (orchestrator resource change, recorded in the LOG, not a Carter decision; sample 2026078 ran under 1 h), one task per fit, with PATH starting at the R env the existing repro fits used: the Snakemake-built env for envs/r_coloc.yml under R4_CONDA_PREFIX (bare Rscript is not on PATH in jobs). Task 1 identifies it from the existing repro jobs' logs or `$SMK --list-conda-envs` and reads the versions from that env's conda-meta (r-base 4.4.2, r-susier 0.14.2, r-coloc 5.2.3; the fit JSONs do not record them); each new fit's policy_hash must equal that of the existing repro fits of the same arm. Before any fit, a split run gives the fitted vs too_many_variants split of the 20: `asthma_pilot_split_commands(...)` returns asthma_pilot_commands' argv with exactly three changes, SUSIE_MAX_VARIANTS=16000 → 0, Rscript → the env's absolute Rscript, and --output → $Q/proxy_split/; every run exits before fitting and records n_variants (pre-panel for repro arms), and a fit counts as too_many_variants where n_variants > 16,000. measurement_argv is not used and not changed (it refuses every repro arm at :88-90, pinned by test_argv_refuses_a_legacy_arm, takes the superseded asthma file from fit_command, and writes under data/r4/tmp/). The 2-fit timed sample is then the region with the most variants among those that will actually fit, in each arm, and gives the per-fit cost: if the projected total exceeds 20 × 40 min, or any fit's MaxRSS exceeds 90% of its own --mem allocation (48G → 45,298,483 KiB; 56G → 52,848,230 KiB), STOP and report the cost. Measured: the k2d sample asthma.EUR.APOE_19q13 (Slurm 2026078, --mem=48G) peaked at MaxRSS 42,565,388 KiB (40.6 GiB, 43.6 GB) in 50:45, over the original 40 GB gate; the routeC sample peaked at 9.1 GiB"
    - "Measured at planning: repro arms apply the 16,000-variant cap before panel restriction, and the corrected asthma EUR file has more than 16,000 rows in the windows of PYHIN1_1q23 (41,040), BMI_5q13_3 (39,606), SLC2A9_urate (27,374), 9p21_CDKN2A (22,998), APOE_19q13 (20,472) and CXADR_F2RL1_6p21 (16,519), so up to 12 of the 20 fits might have exited early as too_many_variants (unknown state in the proxy); FTO_16q12 6,063, MC4R_18q21 6,228, SH2B3_12q24 4,681 and APOL1_22q12 3,947 rows will fit. Measured by the split (Slurm 2025948, pre-panel n_variants): 8 exit early, 12 fit (APOE_19q13 15,136 and CXADR_F2RL1_6p21 13,913 are under the cap). The LOG and DRAFT row report the measured split"
    - "region_contribution_proxy(rscript, repo, exact_purity=True, asthma_fit_root=None, fits_tsv=<path>, policy_path=POLICY_REPRO) is the recorded proxy (Q-DROPASTHMA): asthma pairs stay excluded (PROXY_EXCLUDED_TRAITS) and the 4 other EUR traits are read from the existing repro fits (asthma_fit_root, which reads asthma from the pilot dirs, stays tested by test 5 but is not used for the record); it recomputes every fitted object's purity-filtered set count after the fact with exact purity on the matrix the fit was scored on (Q-PURITY A), by one pinned call: `susieR::susie_get_cs(fit, Xcorr = X_scored, coverage = cov, min_abs_corr = 0.5, dedup = TRUE, squared = FALSE, check_symmetric = TRUE, n_purity = ncol(X_scored))`, plus one auxiliary call with the same arguments except min_abs_corr = 0, which gives the purity of every component susie_get_cs includes (V > 1e-9, non-empty, not a dedup duplicate). cov = fit$sets$requested_coverage, asserted equal to the --credible-set value commands.fit_command passes (config/pipeline.yaml finemap.credible_set); absent or unequal → STOP. eps = policy_path's susie.ld_regularization_eps, read from the YAML (never a literal; absent → STOP). R_fit is the declared Xcorr restricted to the fit's variables in fit order, then `(R + t(R))/2; diag(R) <- 1` as at run_susie_rss.R:1200-1201; Xcorr is the LD panel the fit's JSON declares (ld_file_declared), or the identity matrix iff the fit's JSON records it: ld_status ∈ {identity, ld_missing}, or ld_overlap_zero_fallback TRUE (run_susie_rss.R:1192-1196: no LD matrix → R = diag(n)), or convergence_status contains identity_fallback (run_susie_rss.R:1221). Cross-check: the recorded LD identity (ld_status / ld_overlap_zero_fallback) must agree with the declared panel's `use_identity && is.null(R)` (the k2d_identity panels; run_susie_rss.R:427-442); any disagreement → STOP (measured: bmi.EUR.HLA_6p21 repro_routeC records ld_missing with a real declared panel, out of scope; all 40 repro_k2d_routeC JSONs and the pilot k2d APOE_19q13 record ld_status identity with an identity panel). An identity_fallback fit is identity without the cross-check, since the ladder reaches it with a real panel by design (no in-scope fit has it). When Xcorr is the identity, panel-row mapping is skipped (Q-MEMK2D 2 A): R_fit = I(n) with n = ncol(fit$alpha), the only candidate is the identity (its per-component identity check still runs) and scored_matrix = identity. (k2d identity panels list two rows per allele key, e.g. 16:53800200 and rs9940278, so the unique position + allele lookup leaves members unmapped: 22 of 34 repro_k2d_routeC rows in the dry run, job 2026120, $Q/g157h2/dry_fits.tsv.) Only n_purity differs from fit time for a fit scored on R_fit; it is not true for every fit, because under POLICY_REPRO max_iter_primary = max_iter_retry = 100, so fit2 repeats fit1 and a non_converged fit keeps fit3, scored by susieR 0.14.2 on cov2cor of regularize_ld(R_fit, eps) = sym(R_fit + eps·I) (run_susie_rss.R:25-27, :51-64; the JSON/RDS do not record which). Candidates per fit, in order: identity Xcorr (recorded identity, cross-checked, or identity_fallback) → identity only; converged_primary / converged_max_iter → R_fit only; converged_regularized → C_reg = cov2cor(sym(R_fit + eps·I)) only (fit3 converged, so it is the kept fit); non_converged → C_reg, then R_fit only if C_reg fails (fit_keep <- fit3 %||% fit2, run_susie_rss.R:59-64: an errored fit3 is the only way a non_converged fit was scored on R_fit). A candidate that fails with no next candidate → STOP. X_scored = the first candidate that passes the identity check, recorded per fit as scored_matrix ∈ {identity, panel, regularized, panel_fallback} (panel_fallback = non_converged, R_fit matched after C_reg failed). Identity check, per stored set via sets$cs_index: each stored set equals the recomputed coverage set of the same component; each stored set of ≤ 100 members has recomputed purity equal to its stored sets$purity min.abs.corr within 1e-12; each included component of ≤ 100 members whose index is not in sets$cs_index has purity < 0.5 on X_scored; components of > 100 members are exempt (stored purity was a random 100-member subsample). discriminating = some stored set of 2-100 members is checked (its purity on C_reg is its purity on R_fit / (1+eps): C_reg's off-diagonals are R_fit's scaled by 1/(1+eps) and susieR's get_purity takes the minimum upper-triangle |r|); max_abs_purity_diff = the largest |purity(R_fit) − purity(C_reg)| over those sets; n_sets_exact_alt = the pinned count on the other candidate (C_reg for panel, R_fit for regularized, C_reg for panel_fallback; equal to n_sets_exact for identity). For converged_primary / converged_max_iter fits these three are computed analytically from the R_fit purities (no C_reg is built); for C_reg-candidate fits, directly. discriminating false and n_sets_exact_alt ≠ n_sets_exact → STOP. For a non-identity Xcorr, fit variables are mapped to panel rows with 15.7c's resolve_fit_names (the fit's own sumstats, read in the window the fit JSON records (chrom, start, end): the superseded file for the existing repro fits, the corrected asthma file for the new ones; a sumstats file without REF/ALT columns, e.g. bmi.EUR, gives REF/ALT NA and maps through the panel-rsid override; then a unique CHR:POS; allow_duplicate_rows on for the existing pre-15.5a repro fits only). Only the members of the included components' coverage sets are mapped, since purity reads Xcorr only within a set; other entries of R_fit stay at the identity. A fit with any such member that cannot be mapped gets scored_matrix = unmapped, is counted unknown in the proxy and is listed. fits_tsv gets one row per fitted object: arm, trait, region, convergence_status, n_sets_stored, n_sets_exact, n_sets_exact_alt, n_sets_checked, scored_matrix, discriminating, max_abs_purity_diff, max_abs_resid (largest identity-check residual). With both options off the proxy equals PRE_157H2_REF"
    - "manifests/w3f_region_contribution_proxy.tsv is re-pinned row by row (key = region, contrast; unchanged rows byte-identical; n_pairs_asthma_excluded unchanged, asthma pairs still excluded; each changed row old → new in the LOG); the DRAFT Pre-Paste proxy row and HANDOFF w4a_checkpoint.proposed_lock_values.region_contribution_proxy (old text under region_contribution_proxy_PRE_2026_11_20) carry the new totals and every proxy_flags FLAG line verbatim, labelled \"W3f 15.7h2; repro fits, exact purity on the scored matrix (Q-PURITY A), 4 EUR traits; asthma excluded: the legacy catalog carries the superseded GRCh38 asthma positions, so a corrected-asthma fit through the legacy route mixes builds; never a lock input; n_regions_min stays 7\""
    - "n_regions_min stays 7: measure_fit_eligibility.N_REGIONS_MIN == 7 and decision_rules.yaml unchanged, asserted"
    - "The 9 ids in <new_tests> pass; each of the nine negative controls in <new_tests> (NC-1 to NC-9) was observed RED on its named test case, with __pycache__ cleared under src and tests before each run and after restore and `python -B`, recorded in $Q/negctl_15_7h2.txt, with `git diff --quiet -- src` after restore; FULL vs full_15_7h.xml: 0 removed, added == <new_tests>, 0 outcome changes; 2,691 = 2,638 P / 53 S / 0 F"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/proxy_asthma_pilot_fits_sha256.tsv"
      provides: "20 pilot commands: 12 fits + 8 early exits (JSON + RDS), with sha256, status, set counts and scored_matrix (fitted RDS rows)"
    - path: "tests/ta_r4/test_proxy_exact_purity.py"
      provides: "the 9 tests in <new_tests>"
  key_links:
    - from: "measure_fit_eligibility.asthma_pilot_commands"
      to: "commands.fit_command"
      via: "the arm's argv with --sumstats and --output replaced"
      pattern: "asthma_pilot_commands"
    - from: "measure_fit_eligibility.region_contribution_proxy"
      to: "data/r4/measure_asthma_fix/fits/proxy_asthma_<arm>"
      via: "asthma_fit_root"
      pattern: "asthma_fit_root"
---

<objective>
Carry out Carter's n_regions_min option D (Q-NREG; floor kept at 7) with Q-PROXYA B: run the 20 pilot commands: 12 fits + 8 early exits (JSON + RDS) on
the corrected asthma inputs, then re-measure the region-contribution proxy over the 4 non-asthma EUR traits with exact purity
(15.7f's rule, applied after the fact), and record it. The proxy is read-only with respect to production and
outcome-blind: it is never a lock input and runs no colocalization. Asthma stays excluded (Q-DROPASTHMA): the legacy catalog carries the superseded GRCh38 asthma positions, so a corrected-asthma fit through the legacy route mixes builds.
The 12 fits are pre-lock pilot fits, never a proxy or lock input; 15.7i discloses them.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-PROXY: file `W3f-carter-15-7-Q-PROXY-reply-2026-11-20.txt`, sha256 `f07eece8e40ba0c5e43ac024a21c5fd4b89a00f54bb7b6ef1e5db98a4829bcdf`.
Question text: n_regions_min brief (option D): re-measure the region-contribution proxy after the 15.7 fixes and before the lock? It would use exact purity (15.7f) and the corrected asthma inputs. This is read-only and outcome-blind, the same kind of run as the existing proxy, and it tells you whether the A2_identity 'likely 3 of 10' concern is real. n_regions_min stays 7.
Required label: `Add to 15.7j (Recommended)`

Q-PROXYA: file `W3f-carter-15-7-Q-PROXYA-reply-2026-11-20.txt`, sha256 `6597d02e356f41f8c89fd11716277eefa0317a4308338d14371f614ba49908c5`.
Question text: line 1 of that file after `Question Q-PROXYA (2026-11-20): ` (it contains non-ASCII × and – characters;
the gate reads `--question` from a file extracted byte-for-byte, never retyped).
Required label: `B: Run the 20 asthma fits`

Q-PROXYB: file `W3f-carter-15-7-Q-PROXYB-reply-2026-11-20.txt`, sha256 `651c901c7a28462b686ca738c7f33e3f3a2f14a3a95412899a08deb112826f80`.
Question text: line 1 of that file after `Question Q-PROXYB (2026-11-20): `, read byte-for-byte from the file (as for
Q-PROXYA), never retyped.
Required label: `A: Run as planned (Recommended)`

Q-NREG: file `W3f-carter-15-7-Q-NREG-reply-2026-11-20.txt`, sha256 `2ca9b987cce73317a294db4b024879800d7b5d2dade7d2d49410606fcc05ce18`.
Question text: n_regions_min decision brief: A keep 7 (recommended), B lower to 5 or 3, C add confirmatory regions for A2, D re-measure the proxy after 15.7 before the lock (recommended alongside A).
Required free text: `yes, A and add D to 15.7j and keep 7`

Q-PURITY: file `W3f-carter-15-7h2-purity-matrix-reply-2026-11-21.txt`, sha256 `bf5185dc954e8eb9f246fbddccdedb057908c2b8635ab4aa68b968fdd8f614a6`.
Committed in d2b01ee1. The file does not follow gate_reply.py's format (name and line 1 carry no QID; 8 lines). Gate, with
f = the file: `git ls-files --error-unmatch f`, `git diff --quiet HEAD -- f`, `sha256sum f` equals the value above, and
`[ "$(tail -n 1 f)" = "Carter reply (verbatim, selected option): A: use the scored matrix (Recommended)" ]`; any failing
→ STOP. The file is never edited or renamed. Question text: line 1 after `Question (2026-11-21): `.
Required label: `A: use the scored matrix (Recommended)`

Q-MEMK2D: file `W3f-carter-15-7h2-mem-and-k2d-mapping-reply-2026-11-21.txt`, sha256
`c2783c9b526f29be6a9d576ae89a10e83b8b4bc595e0d5e7b7f153d1acf1030c`, untracked until commit 1c. Not gate_reply.py's format
(two questions; 7 lines). Gate, with f = the file: `sha256sum f` equals the value above,
`[ "$(sed -n 3p f)" = "Carter reply (verbatim, selected option): Raise to 56G (Recommended)" ]` and
`[ "$(sed -n 7p f)" = "Carter reply (verbatim, selected option): A: skip mapping (Recommended)" ]`; any failing → STOP.
The file is never edited or renamed. Question texts: lines 1 and 5 after `Question 1 (2026-11-21): ` / `Question 2 (2026-11-21): `.
Required labels: `Raise to 56G (Recommended)`; `A: skip mapping (Recommended)`

Q-DROPASTHMA: file `W3f-carter-15-7h2-drop-asthma-reply-2026-11-22.txt`, sha256
`072f52793cbc0672bc2261fb34aed17d8bd3212f0df9ebe08f2be71c9a0bb402`, untracked until commit 1d. Not gate_reply.py's format.
Gate, with f = the file: `sha256sum f` equals the value above and
`[ "$(tail -n 1 f)" = "Carter reply (verbatim): yes, drop asthma and check the production catalog" ]`; any failing → STOP.
The file is never edited or renamed. Question text: line 1 after `Question (2026-11-22): `.
Required free text: `yes, drop asthma and check the production catalog`
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@src/python/ta_r4/measure_fit_eligibility.py
@src/python/ta_r4/commands.py
@src/python/ta_r4/arms.py

**Gates** as in <question>; any failure → STOP, nothing run.

**Forbidden:** writing under data/r4/results; any colocalization; production arms or the fire script; changing
N_REGIONS_MIN or decision_rules.yaml; re-running the existing 4-trait repro fits.

**Measured at planning:**
- `measure_fit_eligibility.py:43-51`: PROXY arms (A1: repro_routeC; A2: repro_routeC + repro_k2d_routeC),
  PROXY_EXCLUDED_TRAITS = ("asthma",), N_REGIONS_MIN = 7; `_SETS_R` (:413-418) counts the sets stored at fit time
  (susieR's random 100-member purity for sets > 100).
- 80 existing non-asthma keys: 70 fitted RDS (35 repro_routeC with declared LD data/r4/ld/legacy_repro/EUR, 34 k2d with
  data/r4/ld/k2d_identity/EUR), 9 too_many_variants, 1 missing k2d JSON. Under identity LD every off-diagonal |r| is
  0, so exact and subsampled purity agree there by construction.
- `paths.sumstats_path("asthma", "EUR", <repro arm>)` returns the superseded file (route legacy); the pilot argv
  replaces it with the corrected file explicitly.
- Existing repro asthma fits at the 10 regions: too_many_variants at PYHIN1_1q23, BMI_5q13_3, 9p21_CDKN2A,
  APOE_19q13, SLC2A9_urate (both arms); fitted elsewhere. Earlier LSF maximum per repro fit: 2,243 s, 27 GB.
- Scored matrix (probe, data/r4/tmp/w3f/q157/g157h2/probe_regularized_purity{,_all}.txt): on 6 sets of 5 EUR repro_routeC
  non_converged fits (bmi.SLC2A9_urate ×2, hypertension.APOL1_22q12, hypertension.FTO_16q12, stroke.SLC2A9_urate,
  t2d.FTO_16q12) stored purity / panel purity = 0.9999000100 = 1/(1+eps); the 2 checked sets of converged_primary
  t2d.SH2B3_12q24 match panel R at 0; every other fit has no 2-100-member set (not discriminating). eps: run_susie_rss.R:782
  reads policy susie.ld_regularization_eps (`%||% 1e-4`; the same at 656529a8, the script of the 2026-10-28 repro fits);
  both PROXY arms use POLICY_REPRO (1.0e-4, unchanged since 714df7a5, 2026-10-21); regularize_ld's `eps = 1e-4` is a default
  only. Tolerance: susieR 0.14.2 scores on muffled_cov2cor of (n-1)·R after standardisation (susie_suff_stat), not on R
  itself; on 20 synthetic replicates (m3-r-ld env) the recomputed purity on the matching matrix differed from stored by
  ≤ 3.3e-16 and on the other candidate by ≥ 8.3e-5, so 1e-12 holds and separates the two by > 10 orders.
- RDS vs JSON sets: the proxy reads RDS sets$cs (what coloc.susie reads). For the existing repro fits (2026-10-28, before
  53106f8f) JSON credible_sets were not purity-filtered, so JSON ≥ RDS on 29 ok fits (e.g. stroke.EUR.FTO_16q12 1 vs 0,
  t2d.EUR.SH2B3_12q24 9 vs 5): $MAN/fit_cs_json_vs_rds.tsv, ta-r4-W3-KNOWN-ANSWER-FINDINGS.md §4 and §7 item 10 (fixed in
  53106f8f). JSON credible_sets are not used as a set count.
- Build check (Slurm 2039532, $Q/g157h2/buildcheck/build_check.tsv sha256 651163d3…a63e, committed as
  manifests/w3f_157h2_build_check.tsv). variants_r4 (production catalog): in all 31 regions every rsid joined to the
  production asthma.EUR.grch37_lifted_strand file is at the same position (e.g. APOE_19q13 17,186/17,186, CXADR_F2RL1_6p21
  13,913/13,913), and at 0 positions of the GRCh38 file except NC_IRF4 1,161/1,161 (the builds coincide there): the
  production arms are unaffected. variants_legacy matches the GRCh38 file almost everywhere (CXADR_F2RL1_6p21
  13,914/13,915, 9p21_CDKN2A 18,792/18,793), with partial GRCh37 overlap at a few regions (e.g. APOE_19q13 2,152/19,212).
  run_susie_rss.R windows the sumstats on their own (GRCh37) positions, joins variants_legacy by SNP_ID and overwrites
  CHR/POS (:913-918); data_sources.yaml:66 records the legacy route's input as the GRCh38 file. So the 12 corrected-asthma
  pilot fits mix builds ($Q/g157h2/coordinate_frames.txt). t2d matching the catalog is not evidence either way: t2d
  SNP_IDs are chr:pos strings and t2d is GRCh37.
- Proxy with asthma (job 2037096; $Q/proxy_15_7h2.tsv 2be5f5e3…986f, $Q/proxy_15_7h2_fits.tsv 9c44721f…2775): 81 fits
  rows, 69 non-asthma; the routeC asthma CXADR_F2RL1_6p21 pilot fit came out unmapped. Not recorded as the proxy.
- Current proxy totals: A1_matched likely 8 / unknown 1 / unlikely 1; A2_identity likely 3 / unknown 2 / unlikely 5;
  k not computable (no repro coloc outputs).
</context>

<new_tests>
tests/ta_r4/test_proxy_exact_purity.py; N_new = 9.
1. `test_exact_purity_set_counts_on_a_fixture` (a fixture susie object with one >100-member component whose exact
   purity ≥ 0.5 while its stored set list omits it: count + 1)
2. `test_identity_ld_counts_unchanged_by_exact_purity` (adds two cases, both through the production path
   `region_contribution_proxy(..., exact_purity=True, fits_tsv=...)`, not the IDENTITY_R snippet: (a) a repro_k2d_routeC
   fixture with ld_status identity whose identity panel puts at least one coverage-set member's allele key on two rows (a
   CHR:POS id and an rsid at the same CHR:POS:REF:ALT) → its fits_tsv row has scored_matrix = identity and n_sets_exact ==
   n_sets_stored; (b) a fixture recording ld_status ld_missing with a real declared panel (R non-NULL) → STOP)
3. `test_proxy_default_path_unchanged` (both options off equals PRE_157H2_REF, a literal sha, via `git show`)
4. `test_asthma_pilot_commands_use_the_corrected_input_and_the_pilot_dir` (argv identical to commands.fit_command
   except --sumstats and --output; output outside data/r4/results)
5. `test_proxy_reads_asthma_from_the_pilot_root_and_stops_excluding_it` (adds a case: `region_contribution_proxy(...,
   exact_purity=True, asthma_fit_root=None, fits_tsv=...)` keeps asthma excluded: no asthma row in fits_tsv and
   n_pairs_asthma_excluded equal to the default path's)
6. `test_n_regions_min_is_7`
7. `test_split_argv_equals_the_pilot_argv_except_cap_rscript_and_output` (the three changes only; measurement_argv
   untouched, so test_argv_refuses_a_legacy_arm keeps its outcome)
8. `test_regularised_fit_is_scored_on_the_regularised_matrix` (fixture: a non_converged susie_rss fit (max_iter 2) on
   regularize_ld(R, eps) with a 2-100-member set, eps = 2e-4 from a fixture YAML passed as
   `region_contribution_proxy(..., policy_path=tmp_path / "policy.yaml")`, so a literal 1e-4 fails: identity check passes
   with scored_matrix = regularized, discriminating True and max_abs_purity_diff > 1e-6; with R only as candidate it STOPs)
9. `test_scored_matrix_label_names_the_matrix_that_matched` (fixtures, multi-member ones with a 2-100-member set):
   converged_primary on R → panel, discriminating True, max_abs_purity_diff > 1e-6, and its analytic n_sets_exact_alt equal
   to the pinned call on C_reg; non_converged on C_reg → regularized, discriminating True, max_abs_purity_diff > 1e-6;
   non_converged on R (fit3 errored, fit2 kept) → panel_fallback, discriminating True, max_abs_purity_diff > 1e-6;
   converged_regularized on R → STOP; non_converged on R + 3·eps·I → STOP; a singleton-only non_converged fit → regularized
   with discriminating False; a non-discriminating converged_primary fit (eps 2e-4 via policy_path) whose only sets are
   singletons or > 100 members, one > 100-member set having exact panel purity in [0.5, 0.5·(1+eps)) (e.g. a 101-variant
   equicorrelation block, r = 0.50002), so n_sets_exact_alt ≠ n_sets_exact → STOP)
Negative controls (each edits measure_fit_eligibility.py in the working tree, clears every __pycache__ under src and tests,
runs the named case with `python -B`, must be RED, then restores and clears again):
NC-1 the C_reg candidate removed → test 8 RED. NC-2 the regularized / panel_fallback labels swapped → test 9's
non_converged cases RED. NC-3 the R_fit fallback removed → test 9's panel_fallback case RED. NC-4 panel_fallback allowed for
converged_regularized → test 9's converged_regularized STOP case RED. NC-5 discriminating hard-coded True → test 9's
singleton case RED. NC-6 the discriminating-false / alt-count STOP rule deleted → test 9's non-discriminating STOP case RED. NC-7 panel-row
mapping forced on for identity panels → test 2's case (a) comes back unmapped → RED. NC-8 the recorded-vs-panel identity
cross-check removed → test 2's case (b) does not STOP → RED. NC-9 the asthma exclusion dropped on the exact path
(excluded = () when exact_purity) → test 5's added case RED.
Expected FULL: base full_15_7h.xml (2,682) + 9 = 2,691 = 2,638 P / 53 S / 0 F.
</new_tests>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Gates, DEC, input pins, pilot command builder and exact-purity proxy (RED first)</name>
  <files>.planning/DECISIONS.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7h2-mem-and-k2d-mapping-reply-2026-11-21.txt, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7h2-drop-asthma-reply-2026-11-22.txt, src/python/ta_r4/measure_fit_eligibility.py, tests/ta_r4/test_proxy_exact_purity.py</files>
  <read_first>
    - measure_fit_eligibility.py :1-60, :350-500, :530-600; commands.py :31-53; arms.py
    - run_susie_rss.R :1300-1312 (fit variable names), :1385-1410 (sets)
  </read_first>
  <action>
    0. Gates. `git rev-parse HEAD > $Q/start_15_7h2.txt`; literal `PRE_157H2_REF` in the test. DEC
       `DEC-2026-11-20-ta-r4-proxy-asthma-refit-keep-n-regions-min-7` quoting the four replies, Q-PROXY, Q-PROXYA, Q-PROXYB and Q-NREG (`cat` + `cmp`); it
       records the floor at 7 and that the 20 fits are pre-lock pilot fits. Commit 1 (DECISIONS.md). Done at d1498dff (the
       first execution); on resume verify that commit, do not redo it. Then the Q-PURITY gate (<question>); fail → STOP.
       Commit 1b (DECISIONS.md): DEC `DEC-2026-11-21-ta-r4-proxy-exact-purity-scored-matrix`, quoting the reply file
       verbatim (`cat` + `cmp` of the quoted block against the file), the false premise (the pre-revision text "so only
       n_purity differs from fit time" and its single-matrix identity check, as at d1498dff) and the candidate rule, eps
       source, coverage source and 1e-12 tolerance of the exact-purity must-have.
    1. Measure and pin the inputs into `$Q/proxy_asthma_inputs.tsv` (must_haves); any manifest mismatch → STOP. Identify
       the R env the existing repro fits ran in and record its path and its conda-meta versions; any version other than
       r-base 4.4.2 / r-susier 0.14.2 / r-coloc 5.2.3 → STOP.
    2. RED: the 9 tests (1, 3-9 RED; 2 green by construction; record). GREEN: `asthma_pilot_commands(region_ids,
       out_root)`; `asthma_pilot_split_commands(region_ids, split_root, rscript)`; `region_contribution_proxy(rscript, repo=".", exact_purity=False, asthma_fit_root=None, fits_tsv=None, policy_path=POLICY_REPRO)` and CLI
       flags `--exact-purity` / `--asthma-fit-root` / `--fits-tsv`; the exact path's R snippet per must_haves (scored-matrix
       candidates, eps from policy_path; coverage = fit$sets$requested_coverage asserted == --credible-set), with peak memory bounded (memory rule
       `feedback_dense_matrix_verify_memory_bounded`: at most R_fit and one candidate held at once; rm() + gc() between).
       Negative controls NC-1 to NC-6 (per <new_tests>; __pycache__ cleared before each run and after restore, plus
       `python -B`), each observed RED, then restored; record in $Q/negctl_15_7h2.txt with `git diff --quiet -- src` after
       restore. Commit 2 (code + tests,
       explicit paths). Steps 0-2 and commits 1, 1b, 2 are done (d1498dff, f1f17bef, 265434df); on resume verify, do not redo.
    3. Amendment after Carter's Q-MEMK2D replies. Q-MEMK2D gate (<question>); fail → STOP. Commit 1c (DECISIONS.md + the
       Q-MEMK2D reply file, explicit paths): DEC `DEC-2026-11-21-ta-r4-proxy-k2d-identity-and-56g`, quoting the file
       verbatim (`cat` + `cmp`), recording k2d --mem=56G with the 90%-of-allocation MaxRSS gate (measured 42,565,388 KiB,
       Slurm 2026078) and the identity rule (identity iff the fit JSON records it, cross-checked against the panel; no
       mapping, R_fit = I, scored_matrix = identity; 22 of 34 k2d rows unmapped in job 2026120). It also notes that Carter's Q1 said "12 fits remain … at most 6 are k2d" when 10 remain, 5 of them k2d
       (an overstatement in the conservative direction; the decision stands; the reply file is not edited), and that it
       extends DEC 1b's "identity_fallback → identity only" clause (f1f17bef) to fits whose JSON records identity LD, with
       the recorded-vs-panel cross-check. Then RED: test 2's cases (a) (unmapped on 265434df) and (b) (no STOP); GREEN:
       identity decided from the fit JSON, cross-checked against the panel, mapping skipped, label identity (must_haves);
       NC-7 and NC-8 observed RED and restored as for NC-1 to NC-6;
       tests 1-9 green. Commit 2b (code + tests, explicit paths). Done (563f4753, bcd0310a); on resume verify, do not redo.
    4. Amendment after Carter's Q-DROPASTHMA reply. Q-DROPASTHMA gate (<question>); fail → STOP. Commit 1d (DECISIONS.md +
       the reply file, explicit paths): DEC `DEC-2026-11-22-ta-r4-proxy-drop-asthma-build-mix`, quoting the file verbatim
       (`cat` + `cmp`); it narrows Q-PROXYA B ("Run the 20 asthma fits"): the fits ran, their use in the proxy is
       withdrawn; it records the reason (the legacy catalog carries the superseded GRCh38 asthma positions, so a corrected-asthma fit through the legacy route mixes builds; run_susie_rss.R:913-918,
       data_sources.yaml:66, $Q/g157h2/coordinate_frames.txt) and the build check (Slurm 2039532, build_check.tsv sha256).
       Then test 5's added case (asthma excluded on the exact path) and NC-9 observed RED and restored as for NC-1 to NC-6;
       tests 1-9 green; `git diff --quiet bcd0310a -- src` (no code change). Commit 2c (tests, explicit paths).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_proxy_exact_purity.py tests/ta_r4/test_measure_fit_eligibility.py -q -p no:cacheprovider && git diff --quiet HEAD -- config/ta_r4/decision_rules.yaml</automated>
  </verify>
  <done>Gates passed (incl. Q-PURITY, Q-MEMK2D); commit 1c holds DEC-2026-11-21-ta-r4-proxy-k2d-identity-and-56g (reply quoted, cmp identical, reply file committed); commit 2b holds the identity-panel rule; Q-DROPASTHMA gate passed and commit 1d holds DEC-2026-11-22-ta-r4-proxy-drop-asthma-build-mix (reply quoted, cmp identical, reply file committed); commit 2c holds test 5's exclusion case; commit 1b holds DEC-2026-11-21-ta-r4-proxy-exact-purity-scored-matrix (reply quoted, cmp identical); inputs pinned; 9 tests green after RED; NC-1 to NC-9 observed RED; default proxy unchanged.</done>
</task>

<task type="auto">
  <name>Task 2: Cost check, 20 pilot commands: 12 fits + 8 early exits (JSON + RDS) under Slurm, proxy re-run, records in manifest / DRAFT / HANDOFF</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/proxy_asthma_pilot_fits_sha256.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_region_contribution_proxy.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_157h2_build_check.tsv, .planning/amendments/osf-amendment-r4-DRAFT.md, .planning/HANDOFF.json</files>
  <action>
    0. Split first: run the 20 split commands (asthma_pilot_split_commands; sbatch, cascadelake, `-t 00:30:00`), record
       n_variants and the fitted vs too_many_variants split (n_variants > 16,000), and compare with the planning expectation (up to 12
       early exits); a difference is recorded, not a STOP. Done (Slurm 2025948): 8 early exits, 12 fit.
    1. Cost sample: run 2 of the 20 (the region with the most variants among those that will fit, under repro_routeC and
       under repro_k2d_routeC) as one sbatch array
       (`-p compute -A clintonlab_cpu -q normal --constraint=cascadelake -t 01:00:00`, `--mem=48G`; k2d `--mem=56G` from
       Q-MEMK2D on); record `sacct` Elapsed, MaxRSS and the allocation in the cost record ($Q/cost_15_7h2.tsv and the LOG).
       Project the total from the fitted-region count (early exits take seconds). If the projection exceeds 20 × 40 min, or
       any MaxRSS exceeds 90% of its allocation, STOP and report. Done: Slurm 2026078 ran both at 48G; the k2d
       APOE_19q13 MaxRSS 42,565,388 KiB (84.6% of 48G) in 50:45 stopped the run under the old 40 GB gate; record it with the
       routeC sample (9.1 GiB); both samples are kept (2 of the 12 fits).
    2. Run the other 18 the same way, after Task 1 step 3 (10 fits and 8 early exits; repro_routeC `--mem=48G -t 01:00:00`,
       repro_k2d_routeC `--mem=56G -t 02:00:00`, the -t 02:00:00 being an orchestrator resource change recorded in the LOG
       (sample 2026078 ran in 50:45); any MaxRSS over 90% of its allocation → STOP; one task per fit; liveness by output listing). Every one of the 20 outputs exists,
       status recorded; count fitted vs too_many_variants and compare with step 0's split; a new fit whose
       policy_hash differs from the existing repro fits of its arm → STOP; any other failure → STOP. Manifest the 40 files with sha256, status and stored set count (scored_matrix column filled for the 12 fitted RDS rows from job 2037096's $Q/proxy_15_7h2_fits.tsv, `unmapped` allowed; NA for the JSON rows and the 8 early-exit RDS stubs). Done before Q-DROPASTHMA except the manifest.
    3. Proxy, after Task 1 step 4: `measure_fit_eligibility proxy --rscript <absolute path to the env's bin/Rscript> --exact-purity
       --tsv $Q/proxy_15_7h2_noasthma.tsv --fits-tsv $Q/proxy_15_7h2_noasthma_fits.tsv` (no --asthma-fit-root: asthma
       excluded, Q-DROPASTHMA) under sbatch (`-t 01:00:00 --mem=32G --constraint=cascadelake`). Record, per fitted
       object, stored vs exact set count (k2d must be 0 changes, and every repro_k2d_routeC row scored_matrix = identity, none unmapped), n_sets_exact_alt, scored_matrix and discriminating, the count per scored_matrix
       value (the 5 probe fits must be regularized, t2d.EUR.SH2B3_12q24 repro_routeC panel; otherwise STOP), the totals and the flags.
       No asthma row; the set of (arm, trait, region) keys equals the non-asthma keys of job 2037096's $Q/proxy_15_7h2_fits.tsv
       (sha256 9c44721f…2775; never re-run) and every row equals its counterpart in every column; any difference → STOP.
       Any unmapped row is counted unknown and listed in the LOG. The job 2037096 outputs stay as evidence, sha256 in the LOG.
       Copy $Q/g157h2/buildcheck/build_check.tsv to manifests/w3f_157h2_build_check.tsv (sha256 651163d3…a63e, checked).
    4. Re-pin w3f_region_contribution_proxy.tsv row by row from $Q/proxy_15_7h2_noasthma.tsv; update the DRAFT Pre-Paste proxy row and the HANDOFF line
       per must_haves; test_amendment_text.py green. Commit 3, explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && test "$(grep -vc '^path' .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/proxy_asthma_pilot_fits_sha256.tsv)" = 40 && test "$(grep -vc '^region' .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_region_contribution_proxy.tsv)" = 20 && test -z "$(find data/r4/results -newer data/r4/tmp/w3f/q157/start_15_7h2.txt -name 'asthma.EUR.*' 2>/dev/null)" && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import csv,sys; r=list(csv.DictReader(open('data/r4/tmp/w3f/q157/proxy_15_7h2_noasthma_fits.tsv'),delimiter='\t')); sys.exit(not r or any(x['trait']=='asthma' or x['scored_matrix'] not in ('identity','panel','regularized','panel_fallback','unmapped') for x in r))" && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py -q -p no:cacheprovider</automated>
  </verify>
  <done>Cost checked first; 20 pilot commands (12 fits, 8 early exits) outside the result dirs, manifested with scored_matrix as pre-lock pilot fits, never a proxy input; proxy re-measured over the 4 non-asthma traits with exact purity, rows equal to job 2037096's non-asthma rows; build check committed; manifest, DRAFT row and HANDOFF updated; floor 7.</done>
</task>

<task type="auto">
  <name>Task 3: FULL under Slurm, per-id reconciliation vs full_15_7h.xml, records (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-proxy-asthma-refit-SUMMARY.md</files>
  <action>
    Close per the 15.7 protocol, tag 15_7h2: `$Q/check_15_7h2.py` (removed 0; added == the 9; 0 outcome changes;
    2,691 = 2,638 / 53 / 0). Records: LOG (input pins, Q-PURITY and DEC-2026-11-21-ta-r4-proxy-exact-purity-scored-matrix, Q-MEMK2D and
    DEC-2026-11-21-ta-r4-proxy-k2d-identity-and-56g, Q-DROPASTHMA and DEC-2026-11-22-ta-r4-proxy-drop-asthma-build-mix, the build
    check (Slurm 2039532; sha256 of build_check.tsv / .py / .sh and coordinate_frames.txt), job 2037096's outputs (sha256), NC-1 to NC-9, cost record (incl. Slurm 2026078 MaxRSS; the orchestrator's k2d -t 02:00:00 change), fitted/early-exit split (8 / 12), the 12 pilot fits (24 files) for 15.7i,
    scored_matrix counts with the fits TSV sha256, changed proxy rows), STATE
    (NEXT = 15.7i, which will stop for a v3 F15 wording; NOT PUSHED), PLAN-INDEX COMPLETE, SUMMARY. fsck; commit.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q157/check_15_7h2.py && test -z "$(git status --porcelain -- src tests)"</automated>
  </verify>
  <done>FULL reconciled; records committed; no push.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| pilot fits → outcome blindness | fits on corrected inputs before the lock must stay out of production paths and be disclosed |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-157h2-01 | Tampering | production result dirs | mitigate | outputs under measure_asthma_fix; verify asserts nothing new under data/r4/results |
| T-r4-157h2-02 | Repudiation | pilot fits | mitigate | sha256 manifest; 15.7i recounts and discloses them; never a proxy or lock input (build mix, Q-DROPASTHMA) |
| T-r4-157h2-03 | Denial of service | compute | mitigate | 2-fit cost sample with a STOP threshold before the other 18; MaxRSS over 90% of the allocation (k2d 56G, routeC 48G) → STOP; per-fit wall time routeC 1 h, k2d 2 h (orchestrator change, LOG) |
| T-r4-157h2-04 | Tampering | confirmatory floor | mitigate | N_REGIONS_MIN == 7 test; decision_rules.yaml diff empty |
| T-r4-157h2-05 | Tampering | exact-purity proxy | mitigate | purity recomputed on the scored matrix per fit, labelled; panel_fallback only for non_converged (fit3 errored), converged_regularized is C_reg only; identity decided from the fit JSON and cross-checked against the declared panel, disagreement → STOP; no candidate passes the per-component check within 1e-12 → STOP; discriminating false with differing alt count → STOP; tests 8-9 with NC-1 to NC-9 |
</threat_model>

<verification>
- check_15_7h2.py passes; no file under data/r4/results changed; N_REGIONS_MIN 7.
</verification>

<success_criteria>
- The proxy for the confirmatory floor covers the 4 non-asthma EUR traits with exact purity on the scored matrix, asthma excluded with its reason, recorded before the lock.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-proxy-asthma-refit-SUMMARY.md`
</output>
