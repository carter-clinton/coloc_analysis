---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7h
slug: W3f-null-window-reselection
type: execute
wave: 15.7h
depends_on: ["ta-r4-W3f-qtl-sweep-gwas-pph4"]
gap_closure: true
files_modified:
  - .planning/DECISIONS.md
  - src/python/ta_r4/select_null_windows.py
  - tests/ta_r4/test_null_windows.py
  - tests/ta_r4/test_null_windows_production_pool.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/null_windows_selection.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/null_windows_selection.superseded-2026-10-21.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ukb337k_tiles_sha256.tsv
  - config/ta_r4/regions_r4.csv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_sha256.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_1kg_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_identity_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_1kg_isect_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/panels_EUR_ukb337k_isect_r4.tsv
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-null-window-reselection-SUMMARY.md
autonomous: true
requirements:
  - REQ-NEGATIVE-CONTROLS
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "Gate: gate_reply.py Q-F9 prints \"A: Re-run the selection on the production inputs (Recommended)\" with the <question> text and sha256; otherwise nothing is edited"
    - "The selection driver reproduces the superseded selection byte-for-byte from the superseded inputs (candidates sha256 352c77ecca5061f0e86d5c8ea48f9c388818a8a0b5a335d06cbfab16d12dcce9, 2,865 candidates, the same 10 windows) before it is trusted on the production inputs"
    - "select_null_windows.py runs on the 8 production inputs (sha256 verified against manifests/sumstats_r4_sha256.tsv by path) with the unchanged rule and seed: 2,886 candidates, the 10 windows listed in <objective>; the superseded selection is kept as null_windows_selection.superseded-2026-10-21.tsv (byte-equal to HEAD's file)"
    - "Tile feasibility runs before any rebuild: for each of the 8 changed windows, covering_tiles(chrom, start, end) with no availability filter, compared with the tile manifest. Measured at planning (and by the coordinator): 6 tiles are missing — chr1_231000001_234000001, chr2_201000001_204000001, chr3_33000001_36000001, chr3_190000001_193000001, chr6_81000001_84000001, chr13_41000001_44000001; 1:99750001 and 14:49250001 are covered by on-disk tiles. The 1000G EUR bfiles for chromosomes 1, 2, 3, 6, 13 and 14 are on disk (data/r4/ref/1000G_EUR_Phase3_plink/1000G.EUR.QC.<chr>.{bed,bim,fam})"
    - "The 6 tiles (.npz + .gz each) are fetched with ukb337k_tiles.fetch_tile (fetch_verified; public Broad S3 bucket broad-alkesgroup-ukbb-ld) into their own download dirs, verified by ETag/MD5 and Content-Length plus a magic-byte check before use, and appended to ukb337k_tiles_sha256.tsv (12 rows; every existing row byte-identical). Estimate: ~7 GB (existing .npz mean 1.19 GB), minutes at the earlier fetch rate (~70 MB/s from the manifest's fetched_utc times)"
    - "After the fetch, for every new window region_tiles(...) (the builder's manifest-filtered choice) equals covering_tiles(...) with no filter, so panel content does not depend on which tiles happened to be on disk (6:82750001 would otherwise use the off-centre chr6_80000001_83000001)"
    - "regions_r4.csv is re-emitted with --emit-regions; pair_manifest.tsv is unchanged (its NC_NULL rows carry region ids only; asserted); the NC_NULL catalogs and the 5 EUR panel sets are rebuilt only for the 8 changed windows; their manifest rows are re-pinned and every other row is byte-identical; the panel known-answer gate passes; fit eligibility is re-measured for NC_NULL rows and DRAFT (k) counts updated only if they move"
    - "DRAFT (l) states the re-run (2,886 candidates on the corrected inputs; the superseded 2,865-candidate draw disclosed, 2 of its windows kept)"
    - "The 4 ids in <new_tests> pass; FULL vs full_15_7g.xml reconciled per id; the declared test_null_windows.py spec updates keep their ids and pass"
  artifacts:
    - path: "tests/ta_r4/test_null_windows_production_pool.py"
      provides: "driver identity on the superseded inputs; selection from the production inputs; tile choice independence"
  key_links:
    - from: "manifests/null_windows_selection.tsv"
      to: "config/ta_r4/regions_r4.csv"
      via: "select_null_windows --emit-regions"
      pattern: "NC_NULL"
    - from: "ukb337k_tiles.region_tiles"
      to: "manifests/ukb337k_tiles_sha256.tsv"
      via: "available tiles"
      pattern: "region_tiles"
---

<objective>
Close F9 (CONFIRMED) with Carter's Q-F9 answer A. The null-window pool was built from the superseded inputs
(`null_windows_selection.tsv:15-16`: asthma.AFR `c9a723f3…`, asthma.EUR `22b28075…` with GRCh38 positions, and the
original BMI file), not the production `8828df14…`, `49edfc54…` and `bmi.EUR.r4_alleles` `2f87e771…`.

Measured at planning (read-only, Slurm 2001404 / 2001460; probes in `data/r4/tmp/w3f/q157/planner_probes/f9*`):
identity on the superseded inputs (candidates sha256 352c77…, 2,865, same 10 windows); on the production inputs
2,886 candidates (2,745 shared, 120 dropped, 141 added); the same seed keeps 11:21500001 and 13:71000001 and draws
1:99750001, 1:232000001, 2:202500001, 3:34000001, 3:191500001, 6:82750001, 13:42000001, 14:49250001. No fit has been
run on a null window.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
File `W3f-carter-15-7-Q-F9-reply-2026-11-20.txt`, sha256 `c2cc991553859fa2e40537edfff92677d16439a5956796d08f1fe81d337cc089`.
Question text: The 10 null windows were drawn (seed 20261021) from a 2,865-candidate pool built on the superseded, unlifted asthma inputs. On the corrected inputs the same rule gives 2,886 candidates (2,745 shared). All 10 current windows still qualify, but the same seed now keeps only 2 of 10 (11:21500001 and 13:71000001). No fits have been run on null windows, so either choice is outcome-blind. Re-running needs 6 UKB tiles not on disk (~7 GB, public Broad S3, checksummed). Which?
Required label: `A: Re-run the selection on the production inputs (Recommended)`
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@src/python/ta_r4/select_null_windows.py
@src/python/ta_r4/ukb337k_tiles.py
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-ukb-panels-biallelic-PLAN.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-ukb-panels-biallelic-SUMMARY.md

**Gate.** `$PY $Q/gate_reply.py Q-F9 --question … --sha256 … "A: Re-run the selection on the production inputs
(Recommended)"`. Non-zero → STOP.

**Forbidden:** changing the rule (window, pmax, min_variants, n_select, seed); choosing a new seed; any fit; panels or
catalogs of curated or other NC regions; Track B paths (§B.7); `decision_rules.yaml`.

**Measured at planning:**
- `ukb337k_tiles.region_tiles` (:331-338) keeps only manifest tiles with both .npz and .gz, then `covering_tiles`
  (:63-79) picks the tiles nearest the region centre; the manifest lists 39 tiles (76 file rows), .npz 0.61–2.37 GB.
- pair_manifest.tsv NC_NULL rows hold `region_id` / `region_safe` only. NC_NULL_01..10 are re-assigned in (chr, start)
  order of the new draw.
- tests/ta_r4/test_null_windows.py pins the selection's ids (:156, :187, :215) and the regions file text (:198-200).

**Rebuild pattern:** follow 15.5b (Snakemake via `bin/r4_fire.sh repro …` for the r4 catalog and panel rules, Slurm,
liveness by output listing; per-row re-pin, unchanged rows byte-identical; r4_heavy known-answer gate). The 15.7a fire
allowlist applies to production only.
</context>

<new_tests>
tests/ta_r4/test_null_windows_production_pool.py; N_new = 4.
1. `test_driver_reproduces_the_superseded_selection` (r4_heavy)
2. `test_selection_reproduces_from_the_production_inputs` (r4_heavy)
3. `test_superseded_selection_is_kept`
4. `test_new_window_tiles_do_not_depend_on_what_is_on_disk` (region_tiles == covering_tiles(available=None) for each
   NC_NULL window)
Declared spec update (id kept, passed): `tests.ta_r4.test_null_windows::test_real_selection_reproduces_committed`. It
re-runs the selection on the superseded inputs and compares with `null_windows_selection.tsv`; it is pointed at
`null_windows_selection.superseded-2026-10-21.tsv` (the file those inputs produce). Measured by reading: the other
selection-touching ids (test_committed_selection_shape, test_regions_r4_is_rebuilt_from_sources, test_regions_r4_rows,
test_null_windows_respect_exclusions) check shape or regenerate from the committed files and keep their assertions;
if any of them fails after the re-selection, STOP and report rather than editing it.
Expected FULL: base full_15_7g.xml (2,678) + 4 = 2,682 = 2,629 P / 53 S / 0 F.
</new_tests>

<tasks>

<task type="auto">
  <name>Task 1: Gate, DEC, driver identity, re-selection, tile feasibility and fetch</name>
  <files>.planning/DECISIONS.md, src/python/ta_r4/select_null_windows.py, tests/ta_r4/test_null_windows_production_pool.py, manifests/null_windows_selection.tsv, manifests/null_windows_selection.superseded-2026-10-21.tsv, manifests/ukb337k_tiles_sha256.tsv</files>
  <action>
    0. Gate; `git rev-parse HEAD > $Q/start_15_7h.txt`; DEC `DEC-2026-11-20-ta-r4-null-window-reselection` quoting
       the reply; commit 1.
    1. `select_null_windows.py`: accept `--sha256-manifest` entries keyed by `path` as well as `relative_path`; no rule
       change. RED test 1, then green, under sbatch (`-t 00:30:00 -c 8 --mem=16G`).
    2. Copy HEAD's selection to the superseded name (`cmp`); run on the production inputs into the canonical path;
       assert 2,886 and the 10 windows; a difference → STOP. Tests 2-3.
    3. Feasibility: list `covering_tiles(chr, start, end)` (no filter) for the 8 changed windows against the tile
       manifest into `$Q/tile_feasibility.txt`; check the 1000G bfiles for chromosomes 1, 2, 3, 6, 13, 14. The missing set
       must equal the 6 in must_haves; a difference → STOP.
    4. Network check first: a 1-minute sbatch on a compute node runs `curl -sI` on one tile URL. If compute nodes cannot
       reach S3, fetch from the login node instead (same `fetch_tile` call, `nice`, one tile at a time) and record that.
       Fetch the 6 tiles with `fetch_tile` (sbatch `-t 01:00:00 --mem=8G` if reachable), each into its own new download dir;
       verify before use; append the 12 manifest rows (existing rows byte-identical). Record bytes and wall time.
       Test 4. Commit 2, explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_null_windows_production_pool.py -q -p no:cacheprovider && grep -q "n_candidates	2886" .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/null_windows_selection.tsv && test "$(grep -c '^chr' .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/ukb337k_tiles_sha256.tsv)" = 88</automated>
  </verify>
  <done>Driver identity shown; re-selection reproduces the planning measurement; 6 tiles fetched and verified; tile choice independent of disk state.</done>
</task>

<task type="auto">
  <name>Task 2: Re-emit regions; rebuild NC_NULL catalogs and panels for the 8 windows; re-pin; eligibility; DRAFT</name>
  <files>config/ta_r4/regions_r4.csv, manifests/catalogs_sha256.tsv, the 5 EUR panel manifests, manifests/w3f_fit_eligibility.tsv, tests/ta_r4/test_null_windows.py, .planning/amendments/osf-amendment-r4-DRAFT.md, ta-r4-PLAN-INDEX.md</files>
  <action>
    1. `--emit-regions` → regions_r4.csv; `git diff --quiet -- config/ta_r4/pair_manifest.tsv`. Record the old → new
       window map for NC_NULL_01..10 in the LOG.
    2. Rebuild under Slurm the NC_NULL catalogs and the EUR_1kg_r4, EUR_identity_r4, EUR_1kg_isect_r4, EUR_ukb337k_r4
       and EUR_ukb337k_isect_r4 panels for the 8 changed windows only. Re-pin their rows; every other row byte-identical
       (script diff). Panel known-answer gate (r4_heavy); record counts.
    3. Re-measure fit eligibility for NC_NULL rows (measure_fit_eligibility, cascadelake, no fitting); update rows and,
       only if a count moves, DRAFT (k).
    4. DRAFT: "2,865" appears twice (Pre-Paste table line 42, "Null windows | … 2,865 candidates", and (l) line 126);
       both are updated (line 42 → "2,886 candidates on the corrected inputs; superseded draw from 2,865 kept"). (l): "Null windows: … 10 of the 2,886 candidates on the corrected inputs drawn uniformly with seed 20261021
       (an earlier draw from a 2,865-candidate pool built before the asthma inputs were corrected is superseded; 2 of
       its 10 windows are in the current selection)." PLAN-INDEX §A NC tile list updated. Declared test_null_windows.py
       updates. Commit 3, explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_null_windows_production_pool.py tests/ta_r4/test_null_windows.py tests/ta_r4/test_known_answer_panels.py tests/ta_r4/test_pair_manifest.py tests/ta_r4/test_amendment_text.py -q -p no:cacheprovider && git diff --quiet HEAD -- config/ta_r4/pair_manifest.tsv</automated>
  </verify>
  <done>Only the 8 changed windows rebuilt and re-pinned; known-answer gate passes; DRAFT matches.</done>
</task>

<task type="auto">
  <name>Task 3: FULL under Slurm, per-id reconciliation vs full_15_7g.xml, records (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-null-window-reselection-SUMMARY.md</files>
  <action>
    Close per the 15.7 protocol, tag 15_7h; `$Q/check_15_7h.py` (removed 0; added == the 4; outcome changes only the
    declared ids, still passed; 2,682 = 2,629 / 53 / 0). Records (STATE NEXT = 15.7i; NOT PUSHED). fsck; commit.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q157/check_15_7h.py && test -z "$(git status --porcelain -- src tests config)"</automated>
  </verify>
  <done>FULL reconciled; records committed; no push.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| public S3 download → panels | fetched bytes become LD inputs |
| input correction → control selection | the pool must match the stated rule on the inputs actually used |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-157h-01 | Tampering | downloaded tiles | mitigate | fetch_verified: ETag/MD5, Content-Length, magic bytes; own dirs; manifest rows |
| T-r4-157h-02 | Tampering | seed or rule shopping | mitigate | rule and seed fixed; the re-draw was measured before Carter chose |
| T-r4-157h-03 | Repudiation | superseded draw | mitigate | old selection kept; DRAFT discloses it |
| T-r4-157h-04 | Tampering | rebuild touching other panels | mitigate | per-row re-pin; unchanged rows byte-identical; tile choice test 4 |
</threat_model>

<verification>
- Driver identity; check_15_7h.py passes; curated and other NC rows unchanged in every manifest.
</verification>

<success_criteria>
- The null windows are a seeded draw from the pool the corrected inputs define, built from verified public tiles.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-null-window-reselection-SUMMARY.md`
</output>
