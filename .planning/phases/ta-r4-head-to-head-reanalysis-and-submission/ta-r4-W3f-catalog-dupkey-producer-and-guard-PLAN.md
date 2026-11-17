---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.5a
slug: W3f-catalog-dupkey-producer-and-guard
type: execute
wave: "15.5a"
depends_on: ["ta-r4-W3f-reporting-widening-qtl-sim"]
gap_closure: true
files_modified:
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-dupkey-fix-reply-2026-11-17.txt
  - .planning/DECISIONS.md
  - src/python/ta_r4/catalog_unique_key.py
  - src/python/ta_r4/paths.py
  - src/snakemake/rules/ta_r4_panels.smk
  - tests/ta_r4/test_catalog_unique_key.py
  - src/legacy/region_analysis/scripts/run_susie_rss.R
  - src/python/ta_r4/commands.py
  - tests/ta_r4/test_unique_allele_key_guard.py
  - tests/ta_r4/test_json_cs_equals_fit_sets.py
  - tests/m3/test_source_freeze_pins.py
  - tests/ta_r4/test_live_pins.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_r4_unique_key.tsv
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-eligibility-measurement-and-draft-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-SUSIE-RSS-POLICY
  - REQ-SNAKEMAKE-CI
  - REQ-PATH-PARAMETERIZATION

must_haves:
  truths:
    - "Carter's reply is recorded byte-for-byte (sha256 72a6254a…) in two DEC entries before any code edit; without a matching file the plan stops before touching code"
    - "Every r4 catalog holds one row per normalized (strip+upper) CHR:POS:REF:ALT; multi-allelic sites (same CHR:POS, different alleles, including REF/ALT swaps) are all kept"
    - "The SNP_ID kept for a duplicated key follows one written deterministic rule; every dropped row is kept byte-for-byte in a per-region audit file"
    - "Legacy catalogs, Track B, repro arms and the simulation harness are byte-for-byte / behaviour-for-behaviour unchanged (D-15)"
    - "Residual duplicate risks are measured per fit (arm x trait x region): M1 sumstats 4-key duplicates, M2 duplicated CHR:POS in the post-panel-restriction subset (the key of run_coloc_pair_r4.R:440 DUPLICATE_KEYS), with panel-level counts alongside; any non-zero M1/M2 is a Rule-4 decision for Carter, written as an OPEN row in the DRAFT Pre-Paste that gates the W4a-T3 lock; run_coloc_pair_r4.R and the UKB panels are not changed here"
    - "Under --require-unique-allele-key true, run_susie_rss.R stops non-zero with DUPLICATE_ALLELE_KEYS before the cap check when any normalized 4-key repeats in the fit subset; nothing is deduplicated silently"
    - "Every non-legacy R4 fit argv passes --require-unique-allele-key true; legacy_any arms and Track B do not"
    - "The 31 r4 catalogs are rebuilt in the workflow; the counts reconcile by component: 248,251 byte-exact + 6 case-only = 248,257 dropped; 877,756 − 248,257 = 629,499 kept; catalogs_sha256 r4 rows re-pinned; every catalog-derived panel is byte-identical or the plan stops"
  artifacts:
    - path: "src/python/ta_r4/catalog_unique_key.py"
      provides: "unique_allele_key(lines) -> (kept, dropped, stats); CLI --in --out --dropped"
    - path: "src/snakemake/rules/ta_r4_panels.smk"
      provides: "r4_catalog_raw (collect_region_variants.py, unchanged command) + r4_catalog_unique; r4_catalog constrained to route legacy, shell unchanged"
    - path: "src/legacy/region_analysis/scripts/run_susie_rss.R"
      provides: "--require-unique-allele-key (default false); DUPLICATE_ALLELE_KEYS stop after panel restriction, before the cap"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_r4_unique_key.tsv"
      provides: "per region: n_raw, n_kept, n_dropped_exact, n_dropped_case_ws, n_groups_2, n_groups_3plus, n_chrpos_extra_kept, raw_sha256, dropped_sha256"
    - path: "tests/m3/test_source_freeze_pins.py"
      provides: "R_CODE_REF re-pinned to the guard commit"
  key_links:
    - from: "src/snakemake/rules/ta_r4_panels.smk::r4_catalog_unique"
      to: "ta_r4.catalog_unique_key"
      via: "shell: python -m ta_r4.catalog_unique_key on the raw catalog"
      pattern: "catalog_unique_key"
    - from: "src/python/ta_r4/commands.py::fit_command"
      to: "run_susie_rss.R --require-unique-allele-key"
      via: "argv for every non-legacy arm on CURRENT_SCRIPT, next to --cap-after-ld-restriction"
      pattern: "--require-unique-allele-key"
    - from: "manifests/catalogs_sha256.tsv"
      to: "verify_inputs (in-job) / r4_lock_gate LOCKED_PATHS / test_live_pins"
      via: "r4 rows re-pinned to the rebuilt catalogs"
      pattern: "variants_r4"
---

<objective>
W3f gap closure 15.5a: fix the duplicated-variant defect that stopped plan 15.5 at its Rule-4 checkpoint
(`data/r4/tmp/w3f/elig_20261116/CHECKPOINT_15.5_handback.md`). The r4 catalogs list one CHR:POS:REF:ALT under
two or three SNP_IDs, so `run_susie_rss.R`'s allele-key join copies sumstats rows. Carter chose
"1. Fix both ends (recommended)." The fix has two parts: the producer writes one row per normalized key on the
r4 route, and the frozen script refuses a duplicated key (a guard, not a dedup). Then the catalogs are rebuilt
and re-pinned.

Output: producer module + rule split, a flag-gated guard, RED-first tests with observed negative controls, the
rebuilt catalogs, re-pinned `catalogs_sha256.tsv` and `R_CODE_REF`, and an audit manifest. Everything is
committed and **nothing is pushed**.

**Not fixed here (outside option 1):** `run_coloc_pair_r4.R:439-440` stops on any two fit variants that share a
CHR:POS, and the UKB native panels hold multi-allelic sites. Task 3 measures this per fit (M2), along with
duplicates inside the sumstats (M1). Any non-zero count is a Rule-4 decision for Carter: an OPEN row in the
DRAFT Pre-Paste that gates the W4a-T3 lock. The 15.5 remainder carries it forward and does not resolve it.

**Handoff (decided): re-measurement belongs to 15.5, not 15.5a.** 15.5 owns the measurement module, the eligibility
manifest and the DRAFT. Its remaining work depends on this plan; see PLAN-INDEX.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-producer-cap-fit-names-early-exit-PLAN.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-producer-cap-fit-names-early-exit-SUMMARY.md
@data/r4/tmp/w3f/elig_20261116/CHECKPOINT_15.5_handback.md

Standing rules: PLAN-INDEX §A constants, §B (explicit-path staging; RED first with observed negative controls;
behaviour not text; a count is a claim; no branch switching), §C wave close **except `git push` (forbidden in
15.5a)**. §B.6 (D-28) is lifted only by the DEC from Task 1 step 0, and only for its scope.

Slurm only. Use `sbatch -p compute -A clintonlab_cpu -q normal --constraint=cascadelake -t <limit>` and always
pass `-t`. Rscript is not on PATH in jobs, so use `$RSCRIPT`. Snakemake runs only through `bin/r4_fire.sh`, which
uses `$SMK` and the `config/ta_r4/cluster_slurm` profile (cascadelake).

Forbidden here: push, production fits, repro re-fire, OSF posting, the W4a-T3 lock, and changing n_regions_min.
Write nothing under `data/r4/results`. Scratch goes under `data/r4/tmp/w3f/dupkey/`.

Memory rules that apply: feedback_fix_the_producer_not_just_the_consumer, feedback_green_assertion_needs_a_negative_control,
feedback_aggregate_agreement_hides_component_errors, feedback_a_count_is_a_claim_scope_and_reconcile,
feedback_failsafe_default_is_caller_relative, feedback_keep_edits_simple_no_superfluous_prose,
reference_gpfs_git_object_store_loss, feedback_multi_terminal_staging.

<measured_at_planning>
These were measured by the planner on 2026-11-17 over `data/r4/ld/variants_r4/*.tsv`, read with pandas as
`dtype=str, keep_default_na=False`. Re-derive them; do not copy them.
- 31 catalogs, 877,756 rows. There are 248,251 extra rows on the byte-exact (CHR,POS,REF,ALT) key and 248,257 on
  the strip+upper key. The 6-row difference is **case only**: lowercase alleles on the chr:pos-ID twin, e.g.
  APOE 19:44191717 `g t 19:44191717` vs `G T rs73046624`. There are 0 whitespace cells in any column.
- Duplicate groups by size: 248,239 pairs and 9 triples, so 248,239 + 2×9 = 248,257 extra rows. SNP_ID forms
  per group: {chr:pos, rs} 248,234; {chr:pos, rs, rs} 9; {rs, rs} 5. That makes 14 groups with two or more rsids,
  so the rule needs an rsid tie-break.
- 30 of 31 catalogs carry duplicates; BMI_Xq24 has none. There are 14,799 empty SNP_IDs, none of them in a
  duplicate group.
- After a normalized dedup: 629,499 rows. CHR:POS extra rows drop from 294,400 to 46,143, at 46,132 multi-allelic
  sites. These are preserved.
- There are 17 rows with lowercase alleles: the 6 case twins plus 11 non-duplicates. Those 11 are **not** touched
  here; see the open question in the LOG step.
- The kept row is often not the first occurrence: in 234,677 of the 248,248 duplicate groups the choice rule keeps a
  later row (plan-checker, 2026-11-17). Output order is therefore not "first wins".
- Multi-allelic sites in panels (plan-checker, 2026-11-17, from .bim / panel variants frames):
  - AFR661 / AFR504 / EUR_1kg r4 panels: 0 duplicated CHR:POS (`--biallelic-only strict --snps-only`).
  - EUR_ukb337k_r4: 38 multi-allelic sites in 18 regions.
  - Among the EUR r4 sumstats, only asthma.EUR carries both alleles at 6 of them: BMI_5q13_3 75952721,
    MC4R_18q21 56541713, NC_NULL_06 81514622, NC_SLC24A5 48303816, PYHIN1_1q23 160680184, SLC2A9_urate
    10203217 (SNV + indel). t2d carries one row at each.
  - So A3_ukb asthma fits in those regions (4 confirmatory) would stop at coloc `DUPLICATE_KEYS`.
  - Checker artifacts: `/gpfs_common/share01/clintonlab/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/c8312220-f76b-46f3-96cc-4d31344a5b63/scratchpad/multi.pkl` and `ukb_multi*.py`. Use these only as a cross-check; re-derive the counts in M2.
- Legacy catalogs (`variants_legacy`, 12 files, 816,013 rows) carry 29,363 normalized 4-key extra rows. They are
  **out of scope** and stay byte-unchanged. Repro arms join them on SNP_ID (`--ld-allele-aware false`), which this
  defect does not affect.
</measured_at_planning>

<interfaces>
Producer: `src/legacy/region_analysis/scripts/collect_region_variants.py` (NOT edited). It is shared with Track B
`src/snakemake/rules/ld_reference.smk::collect_region_variants`. It dedups on `SNP::<id>`, else
`POS::chr::pos::ref::alt`, so one variant under two IDs survives twice. It writes TSV `CHR POS REF ALT SNP_ID`,
sorted by CHR, POS.

`src/snakemake/rules/ta_r4_panels.smk:62` `rule r4_catalog`: output `data/r4/ld/variants_{route}/{region}.tsv`,
`route="legacy|r4"`, inputs `CATALOG_SUMSTATS[route]` and `CATALOG_REGIONS_CSV[route]`, `params.region_id`. The
output path comes from `r4paths.catalog_path(route, region_safe)` (`paths.py:66`, `{R4}/ld/variants_{route}/{region}.tsv`).

Consumers of variants_r4. Only these may change behaviour:
- `commands.fit_command` passes `--variant-list` to `run_susie_rss.R`; under `--ld-allele-aware true` this is the
  allele-key join at :836-849.
- `ta_r4_finemap.smk:21` declares it as input.
- `run_qtl_group_r4.catalog()` passes it to `run_coloc_pair_r4.R` / `run_qtl_coloc.R --variant-list`, which builds
  the QTL bridge `bridged_spaces = {catalog_snp_id, catalog_chrpos}` at run_coloc_pair_r4.R:291-301 and drops
  duplicated keys in the chosen space.
- `ta_r4_panels_afr_ukb.smk`:
  - `r4_panel_afr_1kg` uses only the catalog's unique CHR:POS: `awk … | sort -u`, then `--extract range`.
  - `r4_panel_ukb_native` uses `ukb337k_tiles.build_native` with `allowed = set(_allele_keys(cat))`, i.e.
    (POS, frozenset{REF,ALT}). This is **case-sensitive**.
  - `r4_identity_payload_afr` is built from the AFR661 panel.
- `verify_inputs` (in-job) checks the catalogs against `$MAN/catalogs_sha256.tsv`. That manifest is in
  LOCKED_PATHS, alongside `test_lock_gate` N3_EXTRA and R4_DEPENDENCIES.
- `tests/ta_r4/test_live_pins.py` (`CATALOG_DERIVED = AFR661_1kg_r4, AFR504_1kg_r4, AFR661_identity_r4,
  EUR_ukb337k_r4`; 43 catalog rows).
- `measure_fit_eligibility` reads the pins live.

Predicted by construction (to be **verified**, not assumed): dropping duplicate keys leaves the CHR:POS set
unchanged, so the AFR panels should not change. It removes only the 6 lowercase twin keys from the UKB allowed set,
and uppercase twins remain at those positions, so the UKB native panels and stats should not change either. The
expected re-pin is therefore 30 r4 rows of `catalogs_sha256.tsv`, with all panel manifests unchanged.

Frozen script `run_susie_rss.R` (code pin `R_CODE_REF = "1f77128"`; `tests/m3/test_source_freeze_pins.py:71`;
imported by test_finemap_receipt_early_exit.py and test_qtl_coloc_allele_join.py):
- `--cap-after-ld-restriction` option and strict true/false parse: copy this pattern.
- :836-849 allele-key join `subset <- subset[variant_dt, on = c("CHR","POS","REF","ALT"), nomatch = 0][order(idx)]`.
- :1056-1058 `if (!is.null(ld_result$subset_idx)) { subset <- subset[ld_result$subset_idx] }`.
- :1060 `if (cap_after_ld && nrow(subset) > SUSIE_MAX_VARIANTS) {` … too_many_variants early exit.
- The single-line `load_ld_matrix(...)` call must not be touched (tests/m3/test_ld_read_path.py T2.2 regex).
- `K3_PRE_FIX_REF`/`K3_FIX_REF` are differential substrates: never re-pin them.

`commands.fit_command`: when `script == CURRENT_SCRIPT and not _legacy(arm)` it appends
`"--cap-after-ld-restriction", "true"`.

Consumer guard already present: `run_coloc_pair_r4.R:440 DUPLICATE_KEYS`. Its key is **CHR:POS**
(`ss$cp[idx]`), not the 4-key.

Test fixture pattern: `tests/ta_r4/test_cap_after_panel.py`, which imports `build_fixture, _run, _ok` from
test_frozen_script_armed_e2e.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: DEC record; r4-route producer (unique normalized 4-key) with audit output; rule split</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-dupkey-fix-reply-2026-11-17.txt, .planning/DECISIONS.md, src/python/ta_r4/catalog_unique_key.py, src/python/ta_r4/paths.py, src/snakemake/rules/ta_r4_panels.smk, tests/ta_r4/test_catalog_unique_key.py</files>
  <read_first>
    - .planning/DECISIONS.md entries DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze and DEC-2026-11-04-ta-r4-w3f-fix-all (format)
    - data/r4/tmp/w3f/elig_20261116/CHECKPOINT_15.5_handback.md, "Decision needed" item 1
    - src/legacy/region_analysis/scripts/collect_region_variants.py; src/snakemake/rules/ta_r4_panels.smk lines 1-90; src/python/ta_r4/paths.py
    - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R lines 280-305 (QTL bridge key spaces)
  </read_first>
  <behavior>
    unique_allele_key works on raw TSV lines. The header is kept, and kept lines are byte-identical to their input
    lines in input order.
    - The key is (strip(CHR) with a leading chr/CHR removed, int(strip(POS)), strip(REF).upper(), strip(ALT).upper()).
    - Choice rule within a key group, applied in order:
      1. Rank by SNP_ID form: `^rs[0-9]+$` < `^[0-9XYMT]+:[0-9]+$` < other non-empty < empty.
      2. Among rsids, the smallest integer.
      3. A row whose CHR/POS/REF/ALT bytes already equal their normalized form.
      4. The lexicographically smallest SNP_ID.
      5. First occurrence.
    - Fixture cases:
      - (a) chr:pos + rs, byte-exact twins → keep rs; class exact.
      - (b) `g t 19:1` + `G T rs5` → keep the rs row; class case_ws.
      - (c) A whitespace twin (` G` in REF) → class case_ws.
      - (d) Same CHR:POS, ALT C vs ALT T → both kept.
      - (e) Same CHR:POS, A/G vs G/A (REF/ALT swap) → both kept. A different ordered key is not a duplicate.
      - (f) Triple chr:pos + rs200 + rs100 → keep rs100.
      - (g) rs+rs → keep the smaller.
      - (h) Empty SNP_ID + chr:pos → keep chr:pos.
      - (i) Lowercase twins, neither an rsid → keep the uppercase row.
    - An input with no duplicates gives output bytes == input bytes.
    - Multiset identity: sorted(kept body lines + dropped body lines) == sorted(input body lines).
    - The set of normalized keys in kept == the set in input.
    - Dropped file: TSV `CHR POS REF ALT SNP_ID kept_SNP_ID class`. The first five columns are the original line's
      bytes; class is exact or case_ws. Stats: n_raw, n_kept, n_dropped_exact, n_dropped_case_ws, n_groups_2,
      n_groups_3plus, n_chrpos_extra_kept.
    - Missing columns or a non-integer POS raise and name the line number. Nothing is dropped silently.
  </behavior>
  <action>
    0. BLOCKING PRECONDITION. Do this before any code edit.
       - `sha256sum $P/W3f-carter-dupkey-fix-reply-2026-11-17.txt` must print
         `72a6254ade39b0180b241725be2bf4d981ae1fc2f5b8a5a303a496bce8846653`, and `od -c` must show exactly
         `1. Fix both ends (recommended).\n`.
       - The hand-back must hash to `cb52ce1a8ad5b7e8dd4020ad064e022b7998bdeca2716be5eb6806423f0d5ebd`.
       - If either check fails, STOP: write nothing and report.
       - Otherwise append two entries to the END of `.planning/DECISIONS.md` (append-only). Each cites the reply's
         file path and sha256, and quotes the reply byte-for-byte:
         - `## 2026-11-17 — DEC-2026-11-17-ta-r4-catalog-unique-allele-key: r4 catalogs carry one row per normalized CHR:POS:REF:ALT; run_susie_rss.R refuses a duplicate (Carter)`
           - Quote hand-back item 1 (lines 109-111) byte-for-byte, including the backticks around `catalogs_sha256` and
             `R_CODE_REF` on line 110. Copy it with `sed -n '109,111p'`; never retype it. Cite the hand-back sha256.
           - State the choice rule above, and that alternates are not kept in the catalog. The 5-column schema is
             unchanged, because every consumer reads it; alternates go in the audit file
             `data/r4/ld/variants_r4_dropped/<region>.tsv`, whose sha is in `$MAN/catalogs_r4_unique_key.tsv`.
           - State that the kept row is often not the first occurrence (234,677 of 248,248 groups), so the
             choice rule, not file order, decides it.
           - Reason for preferring the rsid: in the QTL bridge the chr:pos form is always recoverable as the
             catalog_chrpos space, but an rsid is not.
           - Scope: r4 route only. `collect_region_variants.py`, the legacy catalogs and Track B are unchanged
             (D-15). The legacy catalogs' 29,363 duplicates are recorded as out of scope.
         - `## 2026-11-17 — DEC-2026-11-17-run-susie-rss-unique-allele-key-guard-unfreeze: D-28 lifted once for the duplicate-key guard in run_susie_rss.R`
           - The reply authorizes the unfreeze by selecting option 1, whose text names "a run_susie_rss.R unfreeze,
             as with N1, and an R_CODE_REF re-pin".
           - Scope: new option `--require-unique-allele-key` (default `false`). With `true`, the script stops non-zero
             with `DUPLICATE_ALLELE_KEYS` when any normalized (CHR,POS,REF,ALT) repeats in the fit subset, checked
             after the panel restriction and before the post-restriction cap. Nothing is dropped.
           - Why the flag defaults to false (justification for not making the guard unconditional):
             `config/pipeline.yaml` sets `ld_read_path.allele_aware: true`, so Track B allele-aware fits read
             legacy-builder catalogs that also carry duplicates. An unconditional guard would stop Track B, which
             D-15 forbids.
           - Repro arms run with `--ld-allele-aware false`, so they never take the allele-key join. The simulation
             harness does not pass the flag.
           - Nothing else changes; D-28 is otherwise in force. Re-pin `R_CODE_REF` to the guard commit.
       - Commit the reply file and DECISIONS.md (explicit paths):
         `docs(ta-r4-W3f): Carter's dup-key decision (DEC catalog unique key; D-28 lift for the guard)`.
    1. Baseline, before any edit: run `$QUICK`, `tests/ta_r4/test_in_job_gate.py` and
       `tests/ta_r4/test_frozen_script_armed_e2e.py`, and save the per-id outcomes to
       `data/r4/tmp/w3f/dupkey/baseline_t1.txt`. The e2e file is r4_heavy, so run it in
       `sbatch --wait -p compute -A clintonlab_cpu -q normal --constraint=cascadelake -t 01:00:00 --mem=16G`.
       RED: write tests/ta_r4/test_catalog_unique_key.py (quick, not r4_heavy) with the behaviours above and a CLI
       round-trip in `tmp_path`. Run it and paste the ImportError/failures.
    2. Implement `src/python/ta_r4/catalog_unique_key.py`:
       - `unique_allele_key(lines) -> (kept_lines, dropped_rows, stats)`, line-level, using the csv module with
         `delimiter="\t"` and no pandas re-serialisation.
       - CLI: `python -m ta_r4.catalog_unique_key --in RAW --out OUT --dropped DROPPED`. It writes `OUT.part` and
         renames it, and prints the stats as one JSON line.
       - In paths.py add `catalog_raw_path(region_safe)` → `{R4}/ld/variants_r4_raw/{region_safe}.tsv` and
         `catalog_dropped_path(region_safe)` → `{R4}/ld/variants_r4_dropped/{region_safe}.tsv`.
    3. Rule split in ta_r4_panels.smk:
       - Constrain `r4_catalog` to `route="legacy"`. Leave its shell, inputs and params byte-unchanged, so the
         legacy outputs see no code or params trigger.
       - Add `rule r4_catalog_raw`. Output `catalog_raw_path`. Same command as r4_catalog with
         `CATALOG_SUMSTATS["r4"]` and `CATALOG_REGIONS_CSV["r4"]`.
       - Add `rule r4_catalog_unique`. Input: raw + `src/python/ta_r4/catalog_unique_key.py`. Outputs:
         `catalog_path("r4", region)` + `catalog_dropped_path`. Shell:
         `PYTHONPATH=src/python {PYTHON_BIN} -m ta_r4.catalog_unique_key --in {input.raw} --out {output.catalog} --dropped {output.dropped}`.
       - `R4_CATALOG_TARGETS` is unchanged; the r4 targets stay `catalog_path("r4", s)`.
    4. GREEN. Then run the negative controls below. Observe each failing, then restore the module sha256-identical,
       and paste the outputs.
       - NC-P1: key without strip/upper → (b), (c) and the multiset/key-set case fail.
       - NC-P2: key on CHR:POS only → (d) and (e) fail.
       - NC-P3: rank chr:pos above rs → (a) and (f) fail.
       - NC-P4: re-serialise through pandas → the no-duplicate byte-identity case fails.
       After the rule split, re-run the three baseline suites the same way and require per-id outcomes identical to
       `baseline_t1.txt`, except for the new test file's additions. test_in_job_gate.py:66-68 creates `variants_r4`
       leaves without a raw catalog, so a changed outcome there is the expected failure mode. Any change is
       STOP-and-report before commit, not a fixture edit.
    5. Dry-run only. Run `bash bin/r4_fire.sh repro repro_routeC -n` on these targets:
       - the 31 `catalog_path("r4")`;
       - the 12 `catalog_path("legacy")`;
       - every `panel_path("repro_routeC", s, "EUR"|"AFR")`;
       - every `panel_path("repro_k2d_routeC", s, a)` (k2d_identity).
       Paste the per-rule job counts. Expected: r4_catalog_raw 31, r4_catalog_unique 31, and **0 jobs** for every
       legacy, repro and k2d target.
       Also run Snakemake's code- and params-change listings over the same legacy, repro and k2d targets
       (`--list-code-changes`, `--list-params-changes`; confirm the 7.32 spellings with `$SMK --help`) and paste
       both. They must list none of those outputs. Anything else means STOP and report.
    6. Commit with explicit paths: catalog_unique_key.py, paths.py, ta_r4_panels.smk and the test, as
       `feat(ta-r4-W3f): r4 catalogs one row per normalized allele key (producer; DEC-2026-11-17-ta-r4-catalog-unique-allele-key)`.
       Run `git fsck --connectivity-only` before and after.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_catalog_unique_key.py -q -rs && sha256sum .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-dupkey-fix-reply-2026-11-17.txt && grep -c "^## 2026-11-17 — DEC-2026-11-17-" .planning/DECISIONS.md</automated>
  </verify>
  <acceptance_criteria>
    - The reply sha256 prints `72a6254a…6653`. The DEC heading count is 2. `git diff HEAD~2 -- .planning/DECISIONS.md | grep -c '^-[^-]'` prints 0, so the file is append-only.
    - The test file passes. The RED output and NC-P1..NC-P4 failures are pasted in the SUMMARY.
    - The dry-run lists 0 legacy `r4_catalog` jobs, with per-rule counts pasted.
    - `git show --stat` of the producer commit lists exactly the 4 code/test files.
  </acceptance_criteria>
  <done>The r4 route has a producer that writes one row per normalized allele key and keeps every dropped row. Legacy and Track B production paths are untouched.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Guard — run_susie_rss.R --require-unique-allele-key (flag-gated), R4 argv, R_CODE_REF re-pin</name>
  <files>src/legacy/region_analysis/scripts/run_susie_rss.R, src/python/ta_r4/commands.py, tests/ta_r4/test_unique_allele_key_guard.py, tests/m3/test_source_freeze_pins.py</files>
  <read_first>
    - src/legacy/region_analysis/scripts/run_susie_rss.R: the option block (`--cap-after-ld-restriction` and its strict parse), lines 795-915 (catalog join), 1040-1100 (panel restriction, cap-after exit)
    - tests/ta_r4/test_cap_after_panel.py and tests/ta_r4/test_frozen_script_armed_e2e.py (fixture builder, `_run`, `_ok`)
    - tests/m3/test_source_freeze_pins.py lines 55-75 (R_CODE_REF, the "update exactly one constant" protocol)
    - the 15.1 SUMMARY (how the N1 code commit and the re-pin commit were split)
  </read_first>
  <behavior>
    The fixture is test_cap_after_panel's panel fixture. Its catalog adds byte-exact chr:pos/rs twins for 3 panel
    variants, a lowercase twin for 1, and a multi-allelic site (same CHR:POS, second ALT; the second allele is
    absent from the panel).
    - Flag true + dup catalog: rc ≠ 0. stderr has `DUPLICATE_ALLELE_KEYS:`, `n_dup_rows=4` and the first keys
      `CHR:POS:REF:ALT`. No .fit.rds with lbf_variable is written.
    - Flag true + the same catalog after `ta_r4.catalog_unique_key`: rc 0. The fit's lbf_variable columns equal the
      distinct panel-restricted count. Neither site's real variant is lost.
    - Flag true + SUSIE_MAX_VARIANTS=0 + dup catalog: `DUPLICATE_ALLELE_KEYS`, **not** too_many_variants. The guard
      runs before the cap, so 15.5's cap-0 measurement detects duplicates.
    - Flag true + clean catalog + a sumstats file with one duplicated 4-key row: `DUPLICATE_ALLELE_KEYS`. The
      property is the fit subset, not the catalog.
    - Flag absent, and `false`, + dup catalog: the result JSON and RDS equal those from `git show 1f77128:<script>`
      run on the same fixture **without** `--require-unique-allele-key`, which 1f77128 rejects. Compare after dropping only timing/path fields; list them. This is the D-15
      behaviour-unchanged differential.
    - `--require-unique-allele-key maybe` exits non-zero with an error naming the flag.
    - `commands.fit_command` over every ARMS entry: non-legacy arms on CURRENT_SCRIPT contain
      `--require-unique-allele-key true`. legacy_any arms and other scripts do not. This check is not heavy.
  </behavior>
  <action>
    1. RED: write tests/ta_r4/test_unique_allele_key_guard.py. The R cases are `r4_heavy` and use `$RSCRIPT`. Run
       them, and every other r4_heavy file in this task, inside `sbatch --wait ... --constraint=cascadelake -t 01:30:00`,
       never on the login node. The argv case is quick. Run it and paste the failures: optparse rejects the flag, and the argv lacks it.
    2. Implement in run_susie_rss.R, minimally:
       - `make_option("--require-unique-allele-key", type = "character", default = "false", ...)`, parsed strictly
         like `--cap-after-ld-restriction`.
       - Immediately after the `if (!is.null(ld_result$subset_idx)) { subset <- subset[ld_result$subset_idx] }`
         block and **before** `if (cap_after_ld && nrow(subset) > SUSIE_MAX_VARIANTS)`, add
         `if (require_unique_key) { k <- paste(toupper(trimws(as.character(subset$CHR))), as.integer(subset$POS), toupper(trimws(as.character(subset$REF))), toupper(trimws(as.character(subset$ALT))), sep = ":"); d <- duplicated(k) | duplicated(k, fromLast = TRUE); if (any(d)) stop(sprintf("DUPLICATE_ALLELE_KEYS: region=%s trait=%s ancestry=%s n_dup_rows=%d of %d; first: %s", opt$region, opt$trait, opt$ancestry, sum(duplicated(k)), length(k), paste(head(unique(k[d]), 5), collapse = ",")), call. = FALSE) }`.
       - `n_dup_rows` counts extra rows (`sum(duplicated(k))`), matching the catalog counts.
       - Do not touch the load_ld_matrix line, and make no other change.
    3. commands.fit_command: append `"--require-unique-allele-key", "true"` right after
       `"--cap-after-ld-restriction", "true"`, in the same non-legacy branch.
    4. GREEN: run the test file plus tests/ta_r4/test_cap_after_panel.py, test_measure_fit_eligibility.py,
       test_json_cs_equals_fit_sets.py and test_frozen_script_armed_e2e.py.
       - Planned spec update: tests/ta_r4/test_json_cs_equals_fit_sets.py:39-46. Its `pre_fix_argv` strips
         `--cap-after-ld-restriction` before running an older substrate script. That script also rejects the new
         flag, so extend `pre_fix_argv` to strip `--require-unique-allele-key` and its value as well. Change nothing
         else in that test.
       - If any other test pinned the exact fit argv, update it to the new argv only. List each such id in the SUMMARY as a
         deliberate spec change; weaken nothing else.
       - Negative controls, each observed failing, then restored (paste):
         - NC-G1: move the guard after the cap check → the cap-0 case fails.
         - NC-G2: replace `stop` with `subset <- subset[!duplicated(k)]` (silent dedup) → the dup-catalog rc case fails.
         - NC-G3: drop the flag from fit_command → the argv case fails.
         - NC-G4: make the default `"true"` → the differential case fails.
    5. Run `$PY -m pytest tests/m3/test_source_freeze_pins.py -q` and expect RED on the R code pin (paste).
       - Commit run_susie_rss.R, commands.py and the test, plus any spec-updated test, as
         `fix(ta-r4-W3f): run_susie_rss.R refuses duplicate allele keys (flag-gated, DEC-2026-11-17-run-susie-rss-unique-allele-key-guard-unfreeze)`.
       - Then set `R_CODE_REF` to that commit's first 7 characters and update the trailing "Re-pinned by" comment.
         Change nothing else: `K3_PRE_FIX_REF`/`K3_FIX_REF` stay.
       - Re-run the pins GREEN. Commit separately as `test(ta-r4-W3f): re-pin R_CODE_REF to <sha7> (dup-key guard)`.
       - Run `git fsck --connectivity-only` before and after each commit.
    6. Run tests/m3/test_ld_read_path.py, test_finemap_receipt_early_exit.py, test_qtl_coloc_allele_join.py,
       tests/ta_r4/test_no_silent_identity.py and test_simulation_harness.py. Outcomes must be identical to before;
       paste the counts. Any changed outcome is STOP-and-report.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && sbatch --wait -p compute -A clintonlab_cpu -q normal --constraint=cascadelake -t 01:30:00 --mem=16G -o data/r4/tmp/w3f/dupkey/verify_t2_%j.out --wrap "cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_unique_allele_key_guard.py tests/ta_r4/test_cap_after_panel.py tests/ta_r4/test_json_cs_equals_fit_sets.py tests/m3/test_source_freeze_pins.py tests/m3/test_ld_read_path.py tests/m3/test_finemap_receipt_early_exit.py -q -rs" && tail -5 data/r4/tmp/w3f/dupkey/verify_t2_*.out</automated>
  </verify>
  <acceptance_criteria>
    - The guard tests pass. RED and NC-G1..NC-G4 are pasted.
    - The guard commit's `git show --stat` lists run_susie_rss.R, commands.py, the new test, and only the listed spec-updated tests. The re-pin commit lists only tests/m3/test_source_freeze_pins.py.
    - The pins are green. Pre-existing frozen-script test outcomes are identical, with counts pasted.
  </acceptance_criteria>
  <done>An R4 fit cannot run on a subset with a repeated allele key. Every other caller behaves as at 1f77128, and the code pin names the authorized commit.</done>
</task>

<task type="auto">
  <name>Task 3: Rebuild the 31 r4 catalogs (+ catalog-derived panels) on Slurm with a byte backup, verify by identity, re-pin, measure fit-level residual risks, close</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_sha256.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_r4_unique_key.tsv, tests/ta_r4/test_live_pins.py, .planning/amendments/osf-amendment-r4-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-eligibility-measurement-and-draft-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/debug/resolved/asthma-eur-grch38-mislabel.md (the 3b1ff91f rebuild: invocation, backup, 91-job dry-run, manifest regeneration via panel_manifest.write_manifest)
    - tests/ta_r4/test_live_pins.py; src/python/ta_r4/verify_inputs.py; $MAN/catalogs_sha256.tsv header
    - data/r4/tmp/w3f/elig_20261116/dup/ (the 15.5 independent join reproduction, Slurm 1946449) and measured_rows.tsv
    - run_susie_rss.R:1104-1121 (panel rsid override of fit names)
  </read_first>
  <action>
    Every hashing, copy and R/pytest step over data/r4 below runs in `sbatch --wait -p compute -A clintonlab_cpu -q normal
    --constraint=cascadelake -t <limit> --mem=<m>`, never on the login node. Logs go to `data/r4/tmp/w3f/dupkey/`.

    1. Back up first.
       - Check space: `df -h /rs1/researchers/c/ckclinto` must show at least 60 GB free. The backup is about 25 GB:
         EUR_ukb337k_r4 12G, AFR661_1kg_r4 6.8G, AFR504_1kg_r4 6.3G, AFR661_identity_r4 13M, plus the stats files.
         Below 60 GB, STOP.
       - Copy, preserving mtimes (`cp -a`):
         - `data/r4/ld/variants_r4/` → `data/r4/tmp/w3f/dupkey/old_variants_r4/`
         - `data/r4/ld/{AFR661_1kg_r4,AFR504_1kg_r4,AFR661_identity_r4,EUR_ukb337k_r4}/` → `data/r4/tmp/w3f/dupkey/old_panels/<panel>/`
         - `data/r4/ld/work/ukb337k/native/*.stats.tsv` → `old_panels/ukb337k_native_stats/`
       - Write SHA256SUMS for each copy. Verify each copy's SHA256SUMS against the live files before going on:
         `pre_panels.sha256` == the backup's sums.
       - Record `pre_untouched.sha256`: every variants_legacy catalog and every repro/k2d/EUR_1kg/identity/isect panel.
       - **STOP branch (restore procedure).** Use it at any later STOP in this task.
         1. Cancel the fire: `squeue -u $USER -o '%i %j' | awk '$2 ~ /^r4\./{print $1}' | xargs -r scancel`. Then
            wait until squeue lists no `r4.*` jobs.
         2. `cp -a` old_variants_r4/ back over `data/r4/ld/variants_r4/`, and each `old_panels/<panel>/` and the
            stats back to their origins.
         3. `sha256sum -c` against the backup SHA256SUMS. This must be 100% OK.
         4. Move `data/r4/ld/variants_r4_raw/` and `variants_r4_dropped/` to `data/r4/tmp/w3f/dupkey/aborted/`.
         5. Re-check `pre_untouched.sha256`.
         6. Do not re-pin anything and do not revert the code commits (never reset). Report the STOP, and the fact
            that a dry-run now lists the rebuild as pending.
    2. Dry-run with `bash bin/r4_fire.sh repro repro_routeC -n`. Targets:
       - every catalog_path("r4");
       - every panel/stats target of r4_panel_afr_1kg, r4_identity_payload_afr and r4_panel_ukb_native;
       - plus, as must-not-run controls: the 12 legacy catalogs, every repro_routeC EUR/AFR panel and every
         k2d_identity target.
       Paste the per-rule counts and the code/params change listings for the control targets.
       - Expected: r4_catalog_raw 31, r4_catalog_unique 31, r4_panel_afr_1kg 20, r4_identity_payload_afr 10,
         r4_panel_ukb_native 30. That is 122 jobs, with 0 for any other rule and the control targets listed by
         neither listing. Anything else means STOP.
       - Then fire the non-control targets without `-n`, under the cascadelake Slurm profile, logging to
         `data/r4/tmp/w3f/dupkey/fire.log`.
       - Judge liveness by the output listing. Done = `122 of 122 steps`, and a following dry-run over all targets,
         controls included, says `Nothing to be done`.
    3. Identity checks, run as one sbatch job. Paste each result. Any failure means the STOP branch.
       - (a) `variants_r4_raw/*.tsv` sha256 == the old pinned r4 rows of catalogs_sha256.tsv, 31/31.
       - (b) Per region: kept lines + dropped lines, as a sorted multiset, == the raw lines. The normalized key set of
         the kept rows == that of the raw rows.
       - (c) Reconcile by component, not by total:
         - raw rows 877,756;
         - dropped exact 248,251 + dropped case_ws 6 = 248,257;
         - kept 629,499, and kept + dropped = raw;
         - groups 248,239×1 + 9×2 = 248,257;
         - SNP_ID group forms 248,234 / 9 / 5;
         - groups whose kept row is not the first occurrence: 234,677 of 248,248;
         - 0 normalized duplicates in any kept catalog;
         - CHR:POS extra in kept = 46,143 at 46,132 sites;
         - BMI_Xq24 kept == raw bytes.
         Every figure must come from a command whose output is pasted. If a component differs from the planning
         measurement, explain it before going on, even when the total matches.
       - (d) All panel .rds and UKB stats are byte-identical to `pre_panels.sha256`. Any difference means the STOP
         branch, with no re-pin.
       - (e) `pre_untouched.sha256` re-checks clean.
    4. Re-pin.
       - Regenerate only the r4 rows of `$MAN/catalogs_sha256.tsv`: n_rows, size_bytes, md5, sha256, keeping the
         header and row order. `git diff` must show exactly 30 changed r4 rows and 0 legacy rows.
       - Write `$MAN/catalogs_r4_unique_key.tsv` with a totals check against (c).
       - Extend tests/ta_r4/test_live_pins.py (r4_heavy). Every r4 catalog must satisfy all three:
         - 0 normalized duplicate keys;
         - kept + dropped == raw as a multiset;
         - the normalized key set of kept == that of raw.
         raw and dropped must also hash to `catalogs_r4_unique_key.tsv`.
       - Observe `test_catalogs_match_manifest` RED before the manifest update and GREEN after. Run both in sbatch and
         paste them.
       - Negative controls, each RED:
         - point the uniqueness test at `old_variants_r4/`;
         - drop one multi-allelic row from a tmp copy of a kept catalog → the key-set test fails.
    5. Residual-risk measurements (one sbatch job, `-t 03:00:00 --mem=48G`). The script lives in
       `data/r4/tmp/w3f/dupkey/` and is not committed. These are measurements, not fixes: do not change
       `run_coloc_pair_r4.R`, the UKB panels or the sumstats.
       - (M2) **Fit level**, per production arm × trait × admissible region (pair_manifest), over the rebuilt
         catalogs.
         - Reproduce the post-panel-restriction fit subset by extending the 15.5 independent join reproduction
           (Slurm 1946449's script) to emit its rows: CHR, POS, REF, ALT, SNP_ID.
         - Validate the reproduction first. Run it on `old_variants_r4/` and require its row count == the script's
           own `n_variants` in `elig_20261116/measured_rows.tsv` on 83/83. Otherwise STOP the measurement and report;
           the commits stand.
         - Then count duplicated CHR:POS (the `run_coloc_pair_r4.R:440` key) per fit and list the keys.
         - Report panel-level duplicated CHR:POS counts per panel and region alongside. The checker expects 0 for the
           1kg panels and 38 sites in 18 regions for EUR_ukb337k_r4.
         - Cross-check against the checker's 6 asthma.EUR A3_ukb sites.
       - (M1) Within-sumstats normalized 4-key extra rows per production (trait, ancestry, region) window, over the
         r4 sumstats `paths.sumstats_path(t, a, arm)`.
       - (M3) QTL-bridge overlap, before (old catalogs) and after, per fit. Derive the fit names as the script does:
         take the reproduced post-restriction subset and apply the panel rsid override (run_susie_rss.R:1104-1121).
         Where the panel `variants` has `^rs[0-9]+$` and the sumstats SNP_ID is chr:pos or blank, the name becomes
         the panel rsid.
         - Compute the overlap with the unique non-empty catalog_snp_id and catalog_chrpos spaces, restricted to
           catalog rows that the allele join binds to panel rows. Report the max per space.
         - A decrease is a FLAG. State in the LOG that this still approximates `ld_allele_join_indices` and is not the
           R function itself.
       - **Rule-4 gate.** If any M1 or M2 count is above 0 for any production fit:
         - Write `FLAG FOR CARTER (Rule 4): <M1|M2> <arm> <trait>.<anc> <region> n=<n> keys=<…>` lines in the LOG.
         - Add one `OPEN (blocks the lock; Carter decision)` row to the DRAFT **Pre-Paste** table, outside the PASTE
           block. It names the fits and confirmatory regions affected and the decision needed: how coloc should treat
           multi-allelic CHR:POS / sumstats duplicates. It gates the W4a-T3 lock.
         - Do not resolve it here. Run test_amendment_text.py, which must pass.
       - M1–M3 do not block this plan's commits.
    6. §C without push:
       - `$QUICK` (record the wall time). Run `$HEAVY`, the pins and `$FULL` in sbatch (`-t 02:00:00`). Record ids,
         passed, skipped and failed vs the last recorded baseline. Allowed: 0 removed ids, 0 outcome changes in
         tests/m3, only additions or listed spec updates in tests/ta_r4.
       - `git fsck`, then commit `catalogs_sha256.tsv`, `catalogs_r4_unique_key.tsv`, `test_live_pins.py` and, if
         written, the DRAFT as
         `fix(ta-r4-W3f): rebuild variants_r4 one row per allele key; re-pin catalogs_sha256 (panels byte-identical)`.
         Run `git fsck` again.
       - Check the 15.5 PLAN frontmatter. The planner made this edit; it is uncommitted. `depends_on` must include
         `ta-r4-W3f-catalog-dupkey-producer-and-guard` and the 2026-11-17 note line must be present. Commit it with
         the LOG.
       - Append a LOG entry with:
         - the DEC ids and commits;
         - dry-run and fire counts; identity checks (a)–(e) with the component reconciliation;
         - M1–M3 and any FLAG lines;
         - QUICK wall time;
         - two out-of-scope findings for Carter: the 11 non-duplicate lowercase-allele rows (probably excluded from
           UKB native panels by the case-sensitive `_allele_keys`), and the 29,363 duplicates in the legacy catalogs
           (read by Track B allele-aware fits);
         - the handoff: "15.5 resumes: re-measure on the rebuilt catalogs, eligibility manifest, DRAFT (k) clause +
           the dup-key Pre-Paste OPEN row resolved + (c)/(m) for the 15.5a commits, 15.5 Task 3, SUMMARY; any M1/M2
           OPEN row stays open until Carter decides and gates W4a-T3".
       - Refresh the W3f line in the STATE.md RESUME block. Commit the LOG, STATE.md and the 15.5 PLAN with explicit
         paths. **Do not push.** Keep the backups until the 15.5 remainder closes.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && sbatch --wait -p compute -A clintonlab_cpu -q normal --constraint=cascadelake -t 02:00:00 --mem=32G -o data/r4/tmp/w3f/dupkey/verify_t3_%j.out --wrap "cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_live_pins.py tests/ta_r4/test_verify_inputs.py tests/ta_r4/test_lock_gate.py tests/ta_r4/test_amendment_text.py -q -rs" && tail -5 data/r4/tmp/w3f/dupkey/verify_t3_*.out && git diff HEAD~3 --stat -- .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ && git status --porcelain -- src tests .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests</automated>
  </verify>
  <acceptance_criteria>
    - The backup sums match the live files before the fire. The fire reached 122 of 122. The final dry-run over all targets, controls included, says "Nothing to be done", and the control targets had 0 jobs and no code/params changes.
    - (a) 31/31. (b) Multiset and key-set identity hold for 31/31. (c) Every component matches or is explained. (d) 0 panel or stats bytes changed. (e) Untouched files are clean.
    - catalogs_sha256.tsv diff: exactly 30 r4 rows changed and 0 legacy rows. No panel manifest changed.
    - test_live_pins: RED before the re-pin and GREEN after; both NCs go RED.
    - The M2 reproduction equals the script's n_variants on 83/83 on the old catalogs. M1/M2 totals are pasted. Every non-zero count has a LOG FLAG line and a DRAFT Pre-Paste OPEN row that gates W4a-T3.
    - FULL: 0 removed ids and 0 tests/m3 outcome changes. Porcelain is empty for the committed paths; nothing is pushed.
  </acceptance_criteria>
  <done>Production inputs carry one row per allele key and are pinned, with the guard as backup. Any duplicate risk that remains at the fit level is measured and on record as a Carter decision that gates the lock. 15.5 can re-measure.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| shared builder → Track B / repro | editing collect_region_variants.py or the legacy rule would move Track B and repro inputs |
| frozen producer → every caller | an edit to run_susie_rss.R can change Track B, repro and simulation outputs |
| catalog → fit subset | a duplicated key silently weights one variant twice in SuSiE |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W3f5a-01 | Tampering | r4 catalog producer | mitigate | line-level dedup; multiset and key-set identity tests; raw == old pins; the dropped rows are kept and hashed |
| T-r4-W3f5a-02 | Tampering | run_susie_rss.R guard | mitigate | flag default false; old-vs-new differential on the fixture; R_CODE_REF re-pinned in a separate commit under a DEC |
| T-r4-W3f5a-03 | Tampering | Track B / legacy catalogs | mitigate | r4_catalog shell unchanged; the dry-run shows 0 legacy jobs; pre_untouched.sha256 re-check |
| T-r4-W3f5a-04 | Repudiation | Carter's decision | mitigate | the reply and the hand-back are hashed and quoted in append-only DEC entries |
| T-r4-W3f5a-05 | Denial of service | panel rebuild overwrite | mitigate | ~25 GB byte backup with verified SHA256SUMS before the fire; scripted restore in the STOP branch |
</threat_model>

<verification>
The producer and guard tests pass, with RED and every negative control observed. The rebuilt catalogs reconcile by
component and are re-pinned. The panels are byte-identical. Track B, legacy and repro are untouched. Everything is
committed and unpushed.
</verification>

<success_criteria>
No R4 fit can carry a duplicated variant, either from the catalog (fixed at the producer) or from anywhere else
(the guard). 15.5 can resume its measurement on pinned inputs.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-catalog-dupkey-producer-and-guard-SUMMARY.md`
</output>
