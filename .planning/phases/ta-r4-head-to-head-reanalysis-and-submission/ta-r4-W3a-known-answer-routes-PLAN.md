---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 11
slug: W3a-known-answer-routes
type: execute
wave: 11
depends_on: ["ta-r4-W2d-apply-review-decisions"]
files_modified:
  - bin/r4_extract_legacy_code.sh
  - src/snakemake/rules/ta_r4_repro.smk
  - src/snakemake/rules/ta_r4_finemap.smk
  - src/python/ta_r4/commands.py
  - src/python/ta_r4/known_answer_compare.py
  - tests/ta_r4/test_known_answer_repro.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/legacy_code_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_repro_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/known_answer_W3a.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-SUSIE-RSS-POLICY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Route L runs the 3dd76df run_susie_rss.R (and every file it sources at that commit), extracted with sha256 to data/r4/legacy_code/; Route C runs the CURRENT frozen script with ld_read_path off and the iter-100 reproduction policy (D-12b, Pattern 4)"
    - "Both routes run the 96 real-LD fits (8 trait-ancestry x 12 regions) on legacy_repro panels and legacy catalogs, and the k2d identity fits on k2d payloads, all stage repro (exempt from the OSF gate per D-05)"
    - "known_answer_W3a.tsv has one row per (fit, route pair) comparing status, n_CS, cs_sizes and the max |ΔPIP| between Route C and Route L, plus columns comparing each to the frozen record (k2d per-fit; Stage-2 aggregates 48 ok / 24 too_many_variants / 18 non_converged / 6 no_variants; 51/96 non-empty)"
    - "Mismatches are recorded as findings, never tuned away; no policy or code is changed in response to a mismatch (§B.10)"
  artifacts:
    - path: "src/snakemake/rules/ta_r4_repro.smk"
      provides: "repro targets for repro_routeC / repro_routeL / repro_k2d_routeC / repro_k2d_routeL"
    - path: "src/python/ta_r4/known_answer_compare.py"
      provides: "per-fit Route C vs Route L vs frozen comparison"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/known_answer_W3a.tsv"
      provides: "the committed known-answer comparison table"
  key_links:
    - from: "src/snakemake/rules/ta_r4_finemap.smk::r4_run_finemap (route legacy)"
      to: "data/r4/legacy_code/run_susie_rss_3dd76df.R"
      via: "ARMS[arm]['route'] == 'legacy' selects the script and the 3dd76df option set"
      pattern: "run_susie_rss_3dd76df"
---

<objective>
Wave 3a reproduces the frozen Track A fits by two independent routes, before any production
comparison: the legacy source code (Route L) and the current frozen code under the reproduction
policy (Route C). The result is a committed per-fit comparison that measures code drift since
2026-04-22 and the reproducibility of the frozen record.

Purpose: D-12(b), D-10, REQ-SUSIE-RSS-POLICY. Mismatches are findings (§B.10).
Output: the legacy code extraction, repro rules, 382 repro fits on /rs1 (96 Route C + 96 Route L + 95 k2d Route C + 95 k2d Route L), a comparison tool + live test + table.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md
@.planning/amendments/TRACK-A-FROZEN-NUMBERS.md
@.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv

<interfaces>
Route L code: `git show 3dd76df:src/legacy/region_analysis/scripts/run_susie_rss.R` (research assumption A1: the last commit
  before the 2026-04-22 fire; alternates to try on mismatch: 0948a76, 1635d37 — record which reproduces)
Route L options (3dd76df): --sumstats --trait --ancestry --method --region --regions-csv --ld-dir --variant-list --credible-set --policy --output
Route C: current script, --ld-authoritative false --ld-allele-aware false (overlay_repro_* sets ld_read_path.ancestries: []),
  policy config/ta_r4/susie_policy_repro_iter100.yaml (max_iter_primary 100, max_iter_retry 100)
Panels: data/r4/ld/legacy_repro/{EUR,AFR}/ (W2a/W2b); k2d payloads data/r4/ld/k2d_identity/; catalogs data/r4/ld/variants_legacy/
Frozen per-fit targets: IDENTITY-LD-K2D-FIT-SUMMARY.tsv (95 rows: trait, ancestry, region_id, status, n_CS, cs_sizes, pip_sum_total, ld_overlap, ...)
Frozen real-LD aggregates: TRACK-A-FROZEN-NUMBERS.md (51/96 non-empty; 48/24/18/6 statuses; H3 33/60, 27/60, 19/60, 41/60)
Per-fit real-LD survivors (spot checks): data/r4/known_answer_survivors/.planning/debug/stage2_narrow_validation/reald_fits/, results/track_a_aggregations/*.tsv
Validator mode for repro arms: legacy_any (records ld_source_class; never fails on LD source)
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Extract the legacy code (Route L) with its dependencies; write the repro rules</name>
  <files>bin/r4_extract_legacy_code.sh, src/snakemake/rules/ta_r4_repro.smk, src/snakemake/rules/ta_r4_finemap.smk, src/python/ta_r4/commands.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/legacy_code_sha256.tsv</files>
  <read_first>
    - `git show 3dd76df:src/legacy/region_analysis/scripts/run_susie_rss.R | grep -n "source(\|library(\|require("` (dependencies to extract)
    - `git log --oneline 3dd76df..08beb4c -- src/legacy/region_analysis/scripts/` (confirm no fit-code commit in between, per research)
    - src/snakemake/rules/ta_r4_finemap.smk, src/python/ta_r4/commands.py, src/python/ta_r4/arms.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-RESEARCH.md §"Pattern 4"
  </read_first>
  <action>
    1. `bin/r4_extract_legacy_code.sh REF` writes `git show REF:<path>` for `run_susie_rss.R` and
       every repo file it `source()`s at that ref (resolved from the grep above) into
       `data/r4/legacy_code/<REF>/<same relative path>`, plus a convenience copy
       `data/r4/legacy_code/run_susie_rss_<REF>.R`. It appends sha256 rows to
       `$MAN/legacy_code_sha256.tsv` (`ref, rel_path, sha256`). Run it for `3dd76df`. If Task 3
       shows a mismatch, also run it for `0948a76` and `1635d37`.
    2. `ta_r4_repro.smk`:
       - Target lists `R4_REPRO_TARGETS(arm)` over the 96 (trait.ancestry × region) combos for
         `repro_routeC`/`repro_routeL`.
       - For the k2d arms, the exact (trait, ancestry, region) set in `IDENTITY-LD-K2D-FIT-SUMMARY.tsv`
         (95 rows). Record which of the 96 combos is absent and why, from the k2d record.
       - The fits use `r4_run_finemap` from W0c, which branches on `ARMS[arm]["route"]`. If W0c did
         not implement the legacy branch fully, implement it in `commands.fit_command` (and, only if
         the rule's shell must change, in `ta_r4_finemap.smk`). That edit is confined to the
         route-legacy branch; the W0c e2e tests and the W0d toy e2e must stay green. If neither file
         needs a change, leave both untouched and say so in the SUMMARY.
       - Legacy panel naming follows `safe_region_id()`, and the legacy invocation passes
         `--ld-dir data/r4/ld/legacy_repro` (or `data/r4/ld/k2d_identity`).
       - HLA_6p21 and BMI_Xq24 use the same panel semantics the frozen fire used. If the frozen
         status for those fits was an early exit (`too_many_variants` / `no_variants`), say so, give
         the source, and verify the reproduced status matches.
    3. Dry-run: `bash bin/r4_fire.sh repro repro_routeC -n <targets>` lists the expected job count.
       The expected count is 96 for each real-LD route and 95 for each k2d route: 96 + 96 + 95 + 95
       = 382 fits in total; paste the counts.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash bin/r4_fire.sh repro repro_routeC -n --quiet 2>&1 | tail -5 && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_frozen_script_armed_e2e.py tests/ta_r4/test_snakemake_toy_e2e.py -q</automated>
  </verify>
  <acceptance_criteria>
    - `$MAN/legacy_code_sha256.tsv` lists `run_susie_rss.R` at 3dd76df plus each sourced dependency
    - the dry-run job counts per arm are pasted and equal 96 / 96 / 95 / 95 (or any deviation is explained from the frozen record)
    - the W0c e2e tests and the W0d toy e2e remain green
  </acceptance_criteria>
  <done>Both reproduction routes are wired and dry-run.</done>
</task>

<task type="auto">
  <name>Task 2: Fire the four reproduction arms on LSF and manifest the fits</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_repro_sha256.tsv</files>
  <read_first>
    - config/ta_r4/cluster_lsf/config.yaml; config/bsub_wrapper.sh
    - memory feedback_lsf_queues, feedback_aou_fanout_gcs_listing_arbiter (liveness = output listing)
  </read_first>
  <action>
    For each arm in `repro_routeC repro_routeL repro_k2d_routeC repro_k2d_routeL`, run
    `nohup bash bin/r4_fire.sh repro <arm> <targets> --jobs 200 > data/r4/logs/fire_<arm>.log 2>&1 &`.
    The arms run sequentially or concurrently; their outputs are disjoint per-arm dirs. Monitor by
    counting `data/r4/results/<arm>/fine_mapping/susie/*.json`. When each completes:
    - Re-run with `-n` and confirm "Nothing to be done".
    - Grep the per-fit receipts for the validator's `ld_source_class` counts.
    - Write `$MAN/fits_repro_sha256.tsv` (`arm, rel_path, sha256`) over every `.json` and `.fit.rds`.
    - Reconcile: rows == 2 × the number of fits per arm, summed.
    Failed jobs: inspect the LSF `.err` under `data/r4/logs/lsf/`. A failure that is a reproduction
    finding (e.g. the legacy code errors on an input) is recorded, not patched around. A pure
    infrastructure failure (node, memory) is retried once with a larger `mem_mb`, and the retry is
    recorded.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && for a in repro_routeC repro_routeL repro_k2d_routeC repro_k2d_routeL; do echo $a $(ls data/r4/results/$a/fine_mapping/susie/*.json 2>/dev/null | wc -l); done</automated>
  </verify>
  <acceptance_criteria>
    - the per-arm JSON counts equal the dry-run job counts from Task 1, or each shortfall is listed by fit id with its error excerpt
    - `$MAN/fits_repro_sha256.tsv` row count == 2 × total JSONs (arithmetic pasted; 2 × 382 = 764 if every fit produced both files, otherwise the early-exit contract is applied and shown)
  </acceptance_criteria>
  <done>All reproduction fits exist on /rs1 and are manifested.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Known-answer comparison tool + live test + committed comparison table; wave-close (W3a)</name>
  <files>src/python/ta_r4/known_answer_compare.py, tests/ta_r4/test_known_answer_repro.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/known_answer_W3a.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv (header + 5 rows)
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (the aggregate block)
    - results/track_a_aggregations/ (per-row tables usable as per-fit known answers; list what each holds)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <behavior>
    - compare(fit_C, fit_L) returns {status_eq, n_cs_eq, cs_sizes_eq, max_abs_dpip}; PIP vectors are aligned by variant id. If variant id sets differ, the result reports that (no NaN-fill)
    - compare_to_k2d(row, fit) returns status/n_CS/cs_sizes equality flags vs the frozen summary row
    - aggregate(fits) returns status counts and the non-empty count, compared with the frozen aggregates
    - Unit tests on synthetic fit dicts cover: identical fits (equal); a PIP perturbation of 1e-9 (NOT equal at the 1e-10 tolerance; max |ΔPIP| reported as 1e-9); a cs_sizes difference; a missing variant
    - Live test (marked r4_heavy; skips only while data/r4/results/repro_routeC is absent): the comparison table has exactly one row per fit present in either route; columns are complete; it does NOT assert equality (§B.10). It does assert the table was produced from the files on disk (row count == union of fit ids)
  </behavior>
  <action>
    Tests RED, then implement `known_answer_compare.py`. Run it to write
    `$MAN/known_answer_W3a.tsv`, then add a summary block to the LOG:
    - the count of fits with Route C ≡ Route L (all of status, n_CS, cs_sizes equal and max |ΔPIP| ≤ 1e-10), and the count that differ;
    - k2d agreement counts for status, n_CS and cs_sizes, each out of 95;
    - reproduced real-LD status counts vs 48 / 24 / 18 / 6 and non-empty vs 51.
    Every count is reconciled: equal + differ == total. If Route L at 3dd76df does not reproduce
    the k2d record, run the alternates `0948a76` / `1635d37` for the k2d route only and record
    which (if any) reproduces. Do not change any policy. Then run §C with label `W3a`, commit type
    `test`.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_known_answer_repro.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - the test passes with the live test RUN (0 skips); the SUMMARY shows the RED run
    - the LOG summary counts reconcile (equal + differ == total for each comparison; arithmetic shown)
    - committed with explicit paths; pushed
  </acceptance_criteria>
  <done>The reproducibility of the frozen record is measured and committed; drift is quantified.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| historical code (git objects) → execution | legacy code is reconstructed from a GPFS repo with known object-loss history |
| known-answer mismatch → analysis choices | the temptation to tune toward the frozen numbers |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W3a-01 | Tampering | legacy code extraction | mitigate | `git fsck --connectivity-only` before extraction; sha256 manifest of the extracted files |
| T-r4-W3a-02 | Repudiation | known-answer tuning | mitigate | the comparison table is committed as produced; §B.10; no policy edits in this plan's files_modified |
| T-r4-W3a-03 | Denial of service | LSF failures | accept | retried once for infrastructure causes, recorded |
</threat_model>

<verification>
Four reproduction arms fitted. The comparison table is committed. Every count reconciled.
</verification>

<success_criteria>
How reproducible the frozen Track A fits are, and how much the code drifted since 2026-04-22, is
a measured, committed fact before any production fit.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3a-known-answer-routes-SUMMARY.md`
</output>
