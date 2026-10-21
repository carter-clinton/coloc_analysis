---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 10
slug: W2d-apply-review-decisions
type: execute
wave: 10
depends_on: ["ta-r4-W2c-qtl-downloads-manifest-and-panel-review"]
files_modified:
  - src/python/ta_r4/arms.py
  - config/ta_r4/overlay_A3_ukb.yaml
  - config/ta_r4/data_sources.yaml
  - src/snakemake/rules/ta_r4_panels_afr_ukb.smk
  - config/ta_r4/qtl_manifest.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_hm3_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/downloads_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "This plan runs only if no config carries locked: true and `python -m ta_r4.signoff verify W2c-T4` exits 0; it reads Carter's decisions from config/ta_r4/review_decisions.yaml, never from prose"
    - "If ukb_native == hm3: EUR_ukb337k_hm3_r4 panels (UKB native restricted to the LDSC HapMap3 SNP list, fetched with a recorded sha256) exist for the same 29 + HLA_6p21 regions, are manifested and read-only, and ARMS['A3_ukb'] + overlay_A3_ukb.yaml point at them; the overlay/isolation tests stay green. If ukb_native == native: nothing changes and the LOG records the no-op (checker W3)"
    - "If qtl_scope != full: config/ta_r4/qtl_manifest.tsv is rebuilt by build_qtl_manifest.py --scope <qtl_scope>; its row count equals the qtl_compute_estimate.tsv row for that scope; test_qtl_manifest stays green. If full: nothing changes (checker W6)"
    - "Both changes land BEFORE the W4b lock commit, so the pre-registration cites the code and manifests actually used"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_hm3_r4.tsv"
      provides: "HM3-restricted UKB native panels (only if ukb_native == hm3)"
  key_links:
    - from: "config/ta_r4/review_decisions.yaml"
      to: "src/python/ta_r4/arms.py ARMS['A3_ukb']"
      via: "ukb_native == hm3 switches panel_source/panel_dir"
      pattern: "EUR_ukb337k_hm3_r4"
---

<objective>
Wave 2d applies Carter's W2c decisions that change inputs: the UKB-native panel handling and the
QTL scope. Both are applied before the analysis lock, so the pre-registration describes the panels
and the QTL row set that production actually uses. Each branch not chosen is a recorded no-op.

Purpose: D-03/D-04 (A3-UKB sensitivity substrate), D-07 (QTL layer scope), checker W3 and W6.
Output: possibly HM3-restricted UKB panels + manifest + arm switch; possibly a restricted QTL manifest.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2c-qtl-downloads-manifest-and-panel-review-SUMMARY.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2b-afr-and-ukb-panels-SUMMARY.md

<interfaces>
config/ta_r4/review_decisions.yaml (W2c T4): {ukb_native: native|hm3, qtl_scope: full|tissues_frozen|eqtl_only|tissues_frozen+eqtl_only, trait facts..., signoff: signoffs/W2c-T4.yaml}
ta_r4.signoff verify W2c-T4 (exit 0 required)
ta_r4.ukb337k_tiles: load_tile, assemble_region, write_rds; rule r4_panel_ukb_native (W2b) — the HM3 rule restricts its output
ta_r4.fetch_verified.fetch_verified(url, dest_dir, md5=, sha256=, size=, magic=)
ta_r4.panel_manifest (W2a) CLI --panel-dir --source --build GRCh37 --n-samples NA --out
build_qtl_manifest.py --scope (W2c)
LDSC HapMap3 list: w_hm3.snplist (public, LDSC distribution; URL rot alternates in memory feedback_url_rot_workarounds)
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Verify the W2c sign-off; apply ukb_native (HM3-restricted UKB native panels, or a recorded no-op)</name>
  <files>src/python/ta_r4/arms.py, config/ta_r4/overlay_A3_ukb.yaml, config/ta_r4/data_sources.yaml, src/snakemake/rules/ta_r4_panels_afr_ukb.smk, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_hm3_r4.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/downloads_sha256.tsv</files>
  <read_first>
    - config/ta_r4/review_decisions.yaml; .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/W2c-T4.yaml
    - src/snakemake/rules/ta_r4_panels_afr_ukb.smk (r4_panel_ukb_native) and src/python/ta_r4/ukb337k_tiles.py
    - data/r4/findings/ukb_native_panel_size.tsv
    - memory feedback_url_rot_workarounds
  </read_first>
  <action>
    0. STOP if any of `config/ta_r4/{coloc_priors,decision_rules,simulation}.yaml` has `locked: true`
       (`$PY -c "import yaml,sys;sys.exit(any(yaml.safe_load(open(f'config/ta_r4/{n}.yaml')).get('locked') for n in ('coloc_priors','decision_rules','simulation')))"`
       must exit 0): W2d changes inputs and may only run before the lock (checker W-2).
       Then `cd src/python && $PY -m ta_r4.signoff verify W2c-T4`. Non-zero → STOP and report; do not
       read review_decisions.yaml.
    1. If `ukb_native == native`: change nothing. Append a LOG line "W2d: ukb_native=native (Carter
       <token date>), no-op". Go to Task 2.
    2. If `ukb_native == hm3`:
       - Fetch `w_hm3.snplist` (LDSC distribution; try the documented URL, then the alternates in
         memory feedback_url_rot_workarounds) with `fetch_verified` into
         `data/r4/downloads/ldsc_w_hm3/` (new empty dir). There is no published checksum; record
         size, sha256, URL and fetch date in `$MAN/downloads_sha256.tsv` and add a `ldsc_w_hm3`
         entry (license, `public: true`) to `config/ta_r4/data_sources.yaml`.
       - Add rule `r4_panel_ukb_hm3` to `ta_r4_panels_afr_ukb.smk`: input the native panel
         `data/r4/ld/EUR_ukb337k_r4/{region_safe}.rds` and the HM3 list; output
         `data/r4/ld/EUR_ukb337k_hm3_r4/{region_safe}.rds` = the native panel's variants whose rsid
         is in the list (rows and columns of R subset in place; variants frame and REF/ALT unchanged).
         The UKB variant table carries rsids; record how many native variants lacked an rsid.
       - Build for the same 29 regions + HLA_6p21 (dry-run first). Write
         `$MAN/panels_EUR_ukb337k_hm3_r4.tsv` with `panel_manifest.py`; `chmod a-w`. Record per-region
         n_var and the count still above 16,000 (a FINDING, not a re-decision).
       - In `arms.py` set `ARMS["A3_ukb"]["panel_source"] = ARMS["A3_ukb"]["panel_dir"] = "EUR_ukb337k_hm3_r4"`
         and update `overlay_A3_ukb.yaml` (chain entry + pin) to match. The native panels stay on
         disk, manifested, unused by production.
       - Run `$PY -m pytest tests/ta_r4/test_overlay_semantics.py tests/ta_r4/test_track_b_isolation.py tests/ta_r4/test_signoffs.py -q`; all green.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import sys,yaml;sys.path.insert(0,'src/python');from ta_r4.arms import ARMS;d=yaml.safe_load(open('config/ta_r4/review_decisions.yaml'));exp={'native':'EUR_ukb337k_r4','hm3':'EUR_ukb337k_hm3_r4'}[d['ukb_native']];assert ARMS['A3_ukb']['panel_dir']==exp,(ARMS['A3_ukb'],exp);print('A3_ukb ->',exp)" && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_overlay_semantics.py tests/ta_r4/test_track_b_isolation.py -q</automated>
  </verify>
  <acceptance_criteria>
    - the verify prints the panel dir that matches Carter's recorded `ukb_native`, and the overlay/isolation tests pass
    - if hm3: `ls data/r4/ld/EUR_ukb337k_hm3_r4/*.rds | wc -l` prints 30 and the manifest has 30 rows; the w_hm3 sha256 is in downloads_sha256.tsv
    - if native: `git diff --quiet HEAD -- src/python/ta_r4/arms.py config/ta_r4/overlay_A3_ukb.yaml` exits 0 and the LOG has the no-op line
  </acceptance_criteria>
  <done>The A3-UKB arm uses the panel class Carter chose, before the lock.</done>
</task>

<task type="auto">
  <name>Task 2: Apply qtl_scope (rebuild the QTL manifest, or a recorded no-op)</name>
  <files>config/ta_r4/qtl_manifest.tsv</files>
  <read_first>
    - config/ta_r4/review_decisions.yaml; manifests/qtl_compute_estimate.tsv
    - src/python/ta_r4/build_qtl_manifest.py; tests/ta_r4/test_qtl_manifest.py
  </read_first>
  <action>
    If `qtl_scope == full`: change nothing; append a LOG no-op line. Otherwise rebuild
    `config/ta_r4/qtl_manifest.tsv` with `build_qtl_manifest.py --scope <qtl_scope>` (the exact
    command used in W2c, with only `--scope` changed). Then run `test_qtl_manifest.py`; its
    determinism test reads the scope from `review_decisions.yaml`, so it regenerates the same file.
    Reconcile: the new row count equals the `n_rows` of that scope in `qtl_compute_estimate.tsv`
    (both numbers pasted). The QTL downloads outside the scope stay on disk and in their manifest.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_qtl_manifest.py -q && awk 'NR>1' config/ta_r4/qtl_manifest.tsv | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - the test passes; the printed row count equals the `qtl_compute_estimate.tsv` n_rows for the recorded scope
  </acceptance_criteria>
  <done>The QTL row set is the one Carter chose, fixed before the lock.</done>
</task>

<task type="auto">
  <name>Task 3: Wave-close (W2d)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>Run §C with label `W2d`, commit type `feat` (or `chore` if both branches were no-ops). Stage only the files this plan actually changed, from its files_modified.</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -q -m "not r4_heavy" && git fsck --connectivity-only 2>&1 | tail -2</automated>
  </verify>
  <acceptance_criteria>
    - QUICK and HEAVY green; tests/m3 unchanged against the baseline; committed with explicit paths; pushed
  </acceptance_criteria>
  <done>W2d committed and pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Carter's recorded decision → inputs | the executor must apply exactly what Carter chose |
| LDSC HM3 list download → panels | an untrusted download changes the A3-UKB variant set |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W2d-01 | Repudiation | decision applied without sign-off | mitigate | `signoff verify W2c-T4` precondition; values read only from review_decisions.yaml (tied to the sign-off by test_signoffs) |
| T-r4-W2d-02 | Tampering | HM3 list | mitigate | fetch_verified (size, magic), sha256 recorded, new empty dir |
| T-r4-W2d-03 | Tampering | silent arm switch | mitigate | verify asserts the A3_ukb panel dir matches the recorded decision; overlay + isolation tests |
| T-r4-W2d-04 | Repudiation | QTL scope set after results | mitigate | runs before any QTL result and before the lock; pure (source, tissue) filter |
</threat_model>

<verification>
The panel class and QTL row set match Carter's recorded decisions; tests green; nothing changes when he chose the defaults.
</verification>

<success_criteria>
Every Carter decision from the data review is applied in code and data before the pre-registration is written.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W2d-apply-review-decisions-SUMMARY.md`
</output>
