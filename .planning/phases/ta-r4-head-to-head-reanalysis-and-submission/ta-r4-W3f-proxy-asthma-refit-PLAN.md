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
  - src/python/ta_r4/measure_fit_eligibility.py
  - tests/ta_r4/test_proxy_exact_purity.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/proxy_asthma_pilot_fits_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_region_contribution_proxy.tsv
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
    - "Gates: Q-PROXY prints \"Add to 15.7j (Recommended)\", Q-PROXYA prints \"B: Run the 20 asthma fits\", Q-PROXYB prints \"A: Run as planned (Recommended)\", and Q-NREG matches the free text \"yes, A and add D to 15.7j and keep 7\", each with its <question> text and sha256; otherwise nothing is edited or run. (Q-PROXY named 15.7j; Q-PROXYA moved the work here, before 15.7i, so the F15 recount sees the new fits)"
    - "Inputs are measured and pinned before any fit: the corrected asthma EUR file data/r4/sumstats/asthma.EUR.grch37_lifted_strand.tsv.bgz (sha256 49edfc54…0c7e2b, manifests/sumstats_r4_sha256.tsv), the legacy-route catalog of each region (paths.catalog_path('legacy', region)), the repro panels (legacy_repro/EUR, k2d_identity/EUR, via the arms' panel manifests), the script and policy the repro arms use (CURRENT_SCRIPT, POLICY_REPRO); every sha256 is checked against its manifest or recorded, in $Q/proxy_asthma_inputs.tsv"
    - "Exactly 20 pre-lock pilot fits are run: asthma × EUR × the 10 confirmatory regions × {repro_routeC, repro_k2d_routeC}, with each arm's own commands.fit_command argv except --sumstats (the corrected file) and --output (data/r4/measure_asthma_fix/fits/proxy_asthma_<arm>/asthma.EUR.<region>.json), so nothing is written under data/r4/results; no receipt, validator, colocalization or production rule runs; the 40 JSON + RDS are sha256-manifested in manifests/proxy_asthma_pilot_fits_sha256.tsv"
    - "The fits run under Slurm: sbatch -p compute -A clintonlab_cpu -q normal --constraint=cascadelake -t 01:00:00 --mem=48G, one task per fit, with PATH starting at the R env the existing repro fits used: the Snakemake-built env for envs/r_coloc.yml under R4_CONDA_PREFIX (bare Rscript is not on PATH in jobs). Task 1 identifies it from the existing repro jobs' logs or `$SMK --list-conda-envs` and reads the versions from that env's conda-meta (r-base 4.4.2, r-susier 0.14.2, r-coloc 5.2.3; the fit JSONs do not record them); each new fit's policy_hash must equal that of the existing repro fits of the same arm. Before any fit, a split run gives the fitted vs too_many_variants split of the 20: `asthma_pilot_split_commands(...)` returns asthma_pilot_commands' argv with exactly three changes, SUSIE_MAX_VARIANTS=16000 → 0, Rscript → the env's absolute Rscript, and --output → $Q/proxy_split/; every run exits before fitting and records n_variants (pre-panel for repro arms), and a fit counts as too_many_variants where n_variants > 16,000. measurement_argv is not used and not changed (it refuses every repro arm at :88-90, pinned by test_argv_refuses_a_legacy_arm, takes the superseded asthma file from fit_command, and writes under data/r4/tmp/). The 2-fit timed sample is then the region with the most variants among those that will actually fit, in each arm, and gives the per-fit cost: if the projected total exceeds 20 × 40 min, or any sample's MaxRSS exceeds 40 GB, STOP and report the cost"
    - "Measured at planning: repro arms apply the 16,000-variant cap before panel restriction, and the corrected asthma EUR file has more than 16,000 rows in the windows of PYHIN1_1q23 (41,040), BMI_5q13_3 (39,606), SLC2A9_urate (27,374), 9p21_CDKN2A (22,998), APOE_19q13 (20,472) and CXADR_F2RL1_6p21 (16,519), so up to 12 of the 20 fits may exit early as too_many_variants (unknown state in the proxy); FTO_16q12 6,063, MC4R_18q21 6,228, SH2B3_12q24 4,681 and APOL1_22q12 3,947 rows will fit. The LOG and DRAFT row report the measured split"
    - "region_contribution_proxy(rscript, repo, exact_purity=True, asthma_fit_root=data/r4/measure_asthma_fix/fits) reads asthma fits from the pilot dirs (asthma pairs no longer excluded) and the other 4 traits from the existing repro fits, and recomputes every fitted object's purity-filtered set count after the fact with exact purity, by one pinned call: `susieR::susie_get_cs(fit, Xcorr = R_fit, coverage = <policy coverage>, min_abs_corr = 0.5, dedup = TRUE, squared = FALSE, check_symmetric = TRUE, n_purity = ncol(R_fit))`, where R_fit is Xcorr restricted to the fit's variables in fit order and coverage is POLICY_REPRO's (the value the fit used), so only n_purity differs from fit time. Xcorr is the LD panel the fit's JSON declares, or the identity matrix for a fit whose convergence_status contains identity_fallback (run_susie_rss.R:1221). Fit variables are mapped to panel rows with 15.7c's resolve_fit_names (the fit's own sumstats: the superseded file for the existing repro fits, the corrected asthma file for the new ones; then the panel-rsid override; then a unique CHR:POS; allow_duplicate_rows on for the existing pre-15.5a repro fits only). A fit with any credible-set candidate member that cannot be mapped is unknown and listed. Identity checks first, per fit: the 95% sets recomputed from alpha equal the stored sets, and for stored sets of ≤ 100 members the recomputed purity equals the stored min.abs.corr within 1e-12; either failing → STOP. With both options off the proxy equals PRE_157H2_REF"
    - "manifests/w3f_region_contribution_proxy.tsv is re-pinned row by row (key = region, contrast; unchanged rows byte-identical; n_pairs_asthma_excluded becomes 0 everywhere; each changed row old → new in the LOG); the DRAFT Pre-Paste proxy row and HANDOFF w4a_checkpoint.proposed_lock_values.region_contribution_proxy (old text under region_contribution_proxy_PRE_2026_11_20) carry the new totals and every proxy_flags FLAG line verbatim, labelled \"W3f 15.7h2; repro fits, exact purity, corrected-asthma pilot fits; never a lock input; n_regions_min stays 7\""
    - "n_regions_min stays 7: measure_fit_eligibility.N_REGIONS_MIN == 7 and decision_rules.yaml unchanged, asserted"
    - "The 7 ids in <new_tests> pass; FULL vs full_15_7h.xml: 0 removed, added == <new_tests>, 0 outcome changes; 2,689 = 2,636 P / 53 S / 0 F"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/proxy_asthma_pilot_fits_sha256.tsv"
      provides: "the 20 pilot fits (JSON + RDS) with sha256, status and set counts"
    - path: "tests/ta_r4/test_proxy_exact_purity.py"
      provides: "the 7 tests in <new_tests>"
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
Carry out Carter's n_regions_min option D (Q-NREG; floor kept at 7) with Q-PROXYA B: run the 20 asthma repro fits on
the corrected asthma inputs, then re-measure the region-contribution proxy over all 5 EUR traits with exact purity
(15.7f's rule, applied after the fact), and record it. The proxy is read-only with respect to production and
outcome-blind: it is never a lock input and runs no colocalization. The 20 fits are pre-lock pilot fits; 15.7i
discloses them.
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
- Current proxy totals: A1_matched likely 8 / unknown 1 / unlikely 1; A2_identity likely 3 / unknown 2 / unlikely 5;
  k not computable (no repro coloc outputs).
</context>

<new_tests>
tests/ta_r4/test_proxy_exact_purity.py; N_new = 7.
1. `test_exact_purity_set_counts_on_a_fixture` (a fixture susie object with one >100-member component whose exact
   purity ≥ 0.5 while its stored set list omits it: count + 1)
2. `test_identity_ld_counts_unchanged_by_exact_purity`
3. `test_proxy_default_path_unchanged` (both options off equals PRE_157H2_REF, a literal sha, via `git show`)
4. `test_asthma_pilot_commands_use_the_corrected_input_and_the_pilot_dir` (argv identical to commands.fit_command
   except --sumstats and --output; output outside data/r4/results)
5. `test_proxy_reads_asthma_from_the_pilot_root_and_stops_excluding_it`
6. `test_n_regions_min_is_7`
7. `test_split_argv_equals_the_pilot_argv_except_cap_rscript_and_output` (the three changes only; measurement_argv
   untouched, so test_argv_refuses_a_legacy_arm keeps its outcome)
Expected FULL: base full_15_7h.xml (2,682) + 7 = 2,689 = 2,636 P / 53 S / 0 F.
</new_tests>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Gates, DEC, input pins, pilot command builder and exact-purity proxy (RED first)</name>
  <files>.planning/DECISIONS.md, src/python/ta_r4/measure_fit_eligibility.py, tests/ta_r4/test_proxy_exact_purity.py</files>
  <read_first>
    - measure_fit_eligibility.py :1-60, :350-500, :530-600; commands.py :31-53; arms.py
    - run_susie_rss.R :1300-1312 (fit variable names), :1385-1410 (sets)
  </read_first>
  <action>
    0. Gates. `git rev-parse HEAD > $Q/start_15_7h2.txt`; literal `PRE_157H2_REF` in the test. DEC
       `DEC-2026-11-20-ta-r4-proxy-asthma-refit-keep-n-regions-min-7` quoting the four replies, Q-PROXY, Q-PROXYA, Q-PROXYB and Q-NREG (`cat` + `cmp`); it
       records the floor at 7 and that the 20 fits are pre-lock pilot fits. Commit 1 (DECISIONS.md).
    1. Measure and pin the inputs into `$Q/proxy_asthma_inputs.tsv` (must_haves); any manifest mismatch → STOP. Identify
       the R env the existing repro fits ran in and record its path and its conda-meta versions; any version other than
       r-base 4.4.2 / r-susier 0.14.2 / r-coloc 5.2.3 → STOP.
    2. RED: the 7 tests (1, 3-7 RED; 2 green by construction; record). GREEN: `asthma_pilot_commands(region_ids,
       out_root)`; `asthma_pilot_split_commands(region_ids, split_root, rscript)`; `region_contribution_proxy(rscript, repo=".", exact_purity=False, asthma_fit_root=None)` and CLI
       flags `--exact-purity` / `--asthma-fit-root`; the exact path's R snippet per must_haves, with peak memory bounded
       (memory rule `feedback_dense_matrix_verify_memory_bounded`). Commit 2 (code + tests).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_proxy_exact_purity.py tests/ta_r4/test_measure_fit_eligibility.py -q -p no:cacheprovider && git diff --quiet HEAD -- config/ta_r4/decision_rules.yaml</automated>
  </verify>
  <done>Gates passed; inputs pinned; 7 tests green after RED; default proxy unchanged.</done>
</task>

<task type="auto">
  <name>Task 2: Cost check, the 20 asthma pilot fits under Slurm, proxy re-run, records in manifest / DRAFT / HANDOFF</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/proxy_asthma_pilot_fits_sha256.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_region_contribution_proxy.tsv, .planning/amendments/osf-amendment-r4-DRAFT.md, .planning/HANDOFF.json</files>
  <action>
    0. Split first: run the 20 split commands (asthma_pilot_split_commands; sbatch, cascadelake, `-t 00:30:00`), record
       n_variants and the fitted vs too_many_variants split (n_variants > 16,000), and compare with the planning expectation (up to 12
       early exits); a difference is recorded, not a STOP.
    1. Cost sample: run 2 of the 20 (the region with the most variants among those that will fit, under repro_routeC and
       under repro_k2d_routeC) as one sbatch array
       (`-p compute -A clintonlab_cpu -q normal --constraint=cascadelake -t 01:00:00 --mem=48G`); record `sacct`
       Elapsed and MaxRSS. Project the total from the fitted-region count (early exits take seconds). If the projection
       exceeds 20 × 40 min, or either MaxRSS exceeds 40 GB, STOP and report.
    2. Run the other 18 the same way (one task per fit; liveness by output listing). Every one of the 20 outputs exists,
       status recorded; count fitted vs too_many_variants and compare with step 0's split; a new fit whose
       policy_hash differs from the existing repro fits of its arm → STOP; any other failure → STOP. Manifest the 40 files with sha256, status and stored set count.
    3. Proxy: `measure_fit_eligibility proxy --rscript <absolute path to the env's bin/Rscript> --exact-purity
       --asthma-fit-root data/r4/measure_asthma_fix/fits --tsv $Q/proxy_15_7h2.tsv` under sbatch (`-t 01:00:00 --mem=32G --constraint=cascadelake`). Record, per fitted
       object, stored vs exact set count (k2d must be 0 changes), the totals and the flags.
    4. Re-pin w3f_region_contribution_proxy.tsv row by row; update the DRAFT Pre-Paste proxy row and the HANDOFF line
       per must_haves; test_amendment_text.py green. Commit 3, explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && test "$(grep -vc '^path' .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/proxy_asthma_pilot_fits_sha256.tsv)" = 40 && test "$(grep -vc '^region' .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_region_contribution_proxy.tsv)" = 20 && test -z "$(find data/r4/results -newer data/r4/tmp/w3f/q157/start_15_7h2.txt -name 'asthma.EUR.*' 2>/dev/null)" && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py -q -p no:cacheprovider</automated>
  </verify>
  <done>Cost checked first; 20 pilot fits outside the result dirs, manifested; proxy re-measured over 5 traits with exact purity; manifest, DRAFT row and HANDOFF updated; floor 7.</done>
</task>

<task type="auto">
  <name>Task 3: FULL under Slurm, per-id reconciliation vs full_15_7h.xml, records (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-proxy-asthma-refit-SUMMARY.md</files>
  <action>
    Close per the 15.7 protocol, tag 15_7h2: `$Q/check_15_7h2.py` (removed 0; added == the 7; 0 outcome changes;
    2,689 = 2,636 / 53 / 0). Records: LOG (input pins, cost sample, fitted/early-exit split, changed proxy rows), STATE
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
| T-r4-157h2-02 | Repudiation | pilot fits | mitigate | sha256 manifest; 15.7i recounts and discloses them |
| T-r4-157h2-03 | Denial of service | compute | mitigate | 2-fit cost sample with a STOP threshold before the other 18 |
| T-r4-157h2-04 | Tampering | confirmatory floor | mitigate | N_REGIONS_MIN == 7 test; decision_rules.yaml diff empty |
</threat_model>

<verification>
- check_15_7h2.py passes; no file under data/r4/results changed; N_REGIONS_MIN 7.
</verification>

<success_criteria>
- The proxy for the confirmatory floor covers all 5 EUR traits on corrected inputs with exact purity, recorded before the lock.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-proxy-asthma-refit-SUMMARY.md`
</output>
