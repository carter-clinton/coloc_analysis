---
phase: m3-aou-afr-ld-panel-build
plan: 07c
type: execute
wave: 3
depends_on: ["07b"]
tags: [ld, occlusion, present-rate, lockstep, sumstats, aou, afr, tdd]
files_modified:
  - src/python/occlusion_present_rate_scan.py
  - src/python/drop_occluded_from_sumstats.py
autonomous: true
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-VALIDATION
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "occlusion_present_rate_scan.scan_present_rate(variants_grch37, sumstats_paths) -> dict keyed by the (chr:int, pos:int) GRCh37 TUPLE, each value {n_traits_present, n_traits_scanned, present_rate, traits_present}, reporting PRESENT-vs-ABSENT rate per occluded variant (k/n) over the 9 public GRCh37 AFR harmonized sumstats (header CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD), auto-detecting CHR/POS cols BY NAME — REQ-PUBLIC-DATA-ONLY (no perimeter, read-only). Unit-covered on synthetic fixtures; the real 9-file scan is a gated integration step."
    - "drop_occluded_from_sumstats(sumstats_path, manifest_path, out_path) -> dict is FILE-IN / FILE-OUT (it READS the sumstats TSV and the manifest TSV and WRITES out_path) and returns the counts dict {n_in, n_dropped, n_out} with the invariant n_in - n_dropped == n_out. It removes EXACTLY the manifest's GRCh37 (CHR,POS) rows (drop-only, no re-key — snp_id_bridge.R (CHR,POS) semantics), logs each dropped coordinate to STDERR, leaves non-occluded rows byte-identical, and is IDEMPOTENT (re-running on its own OUTPUT drops nothing and reproduces the same bytes); prevents orphaning a sumstats-present occluded variant (rs182965575 present 7/9 AFR)."
    - "The exact m3-04 consume-step wiring is a DOCUMENTED deferred hook (finemap.smk:89-93 STALE/SUPERSEDED-PENDING-REPLAN): the reusable filter lands NOW with tests; the wiring is deferred to the m3-04 replan (RESEARCH open-decision #3, checker-approved) — finemap.smk is NOT modified here."
    - "Frozen contracts stay byte-unchanged: `git diff --stat src/snakemake/rules/finemap.smk src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` is EMPTY — no consume wiring, no frozen-contract change; m3-06 condition_ld_matrix.py is NOT touched."
  artifacts:
    - path: "src/python/occlusion_present_rate_scan.py"
      provides: "Genome-wide present-rate-per-ancestry scan of occluded variants over the 9 AFR harmonized GRCh37 sumstats"
      exports: ["scan_present_rate"]
    - path: "src/python/drop_occluded_from_sumstats.py"
      provides: "Reusable manifest-driven (CHR,POS) drop-only lockstep sumstats filter; idempotent; m3-04 consume-wiring deferred"
      exports: ["drop_occluded_from_sumstats"]
  key_links:
    - from: "src/python/drop_occluded_from_sumstats.py"
      to: "src/R/regularization/snp_id_bridge.R"
      via: "(CHR,POS) drop-only membership semantics (no re-key)"
      pattern: "CHR.*POS"
    - from: "src/python/occlusion_present_rate_scan.py"
      to: "data/processed/sumstats_harmonized/*.AFR*.tsv.bgz"
      via: "read-only (CHR,POS) presence scan over the 9 public GRCh37 AFR sumstats"
      pattern: "present_rate"
---

<objective>
Plan **07c of the m3-07 split** — the scientific-cost + lockstep-safety tail. Two tasks:
(T3) the **genome-wide present-rate-per-ancestry scan** (`occlusion_present_rate_scan.py`) — for
each occluded variant, PRESENT-vs-ABSENT rate over the 9 public GRCh37 AFR harmonized sumstats
(the metric that sizes the Angle-1/3 scientific cost);
(T4) the **reusable lockstep sumstats-side drop filter** (`drop_occluded_from_sumstats.py`) —
manifest-driven (CHR,POS) drop-only, idempotent, no re-key; the exact m3-04 consume wiring is a
DOCUMENTED deferred hook (finemap.smk m3-04-W4 is STALE/SUPERSEDED-PENDING-REPLAN).

**Depends on 07b** (`depends_on: ["07b"]`): T3/T4 CONSUME the T2 occlusion manifest (07b), and
their RED tests live in 07a. This plan turns the 07a present-rate + lockstep RED suites GREEN;
its verification is scoped to ITS OWN tests only.

The SCIENCE is settled (policy = exclude-in-lockstep + provenance `42d70167…`; the (CHR,POS)
join impact / rs182965575-present-7/9 hinge check). Do NOT re-litigate. `NaN→0` is DEAD.

Output: `occlusion_present_rate_scan.py`, `drop_occluded_from_sumstats.py` — CI-runnable on
synthetic fixtures; finemap.smk + frozen contracts git-diff-gated.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/amendments/m3_panel_occlusion_policy_decision.md
@.planning/amendments/m3_region1_occlusion_hinge_check.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-07b-W7-span-filter-and-manifest-PLAN.md
@src/R/regularization/snp_id_bridge.R

# 07a authored the RED tests (test_occlusion_present_rate_scan.py, test_occlusion_lockstep_drop.py); 07b
# produced the occlusion manifest T3/T4 consume. This plan makes those two RED suites GREEN. Do NOT edit
# their expectations. m3-07-RESEARCH.md §1(T3/T4), §7 (open-decision #3 — deferred wiring) is the code-path map.

<interfaces>
<!-- Contracts the executor needs. Extracted from the working tree @ m3-W2-aou-deltas. -->

AFR harmonized sumstats (9 files, PUBLIC GRCh37) — data/processed/sumstats_harmonized/*.AFR*.tsv.bgz
header: `CHR  POS  REF  ALT  BETA  SE  P  EAF  N  SNP_ID  TRAIT  ANCESTRY  BUILD`

The present-rate scan prototype (m3_region1_occlusion_hinge_check.md:124-141 — auto-detect CHR/POS, (CHR,POS) window):
```bash
zcat "$f" | awk 'NR==1{for(i=1;i<=NF;i++)h[$i]=i;
  cc=(h["CHR"]?h["CHR"]:1); pc=(h["POS"]?h["POS"]:(h["BP"]?h["BP"]:2)); next}
  {c=$cc; sub(/^chr/,"",c); if(c==<CHR>){if($pc==<POS>)print}}'
```
rs182965575 @ GRCh37 chr1:5982778 is PRESENT in 7/9 AFR sumstats (every trait except stroke) — the orphan T4 prevents.

Panel↔sumstats join (src/R/regularization/snp_id_bridge.R:107-121): membership is (CHR,POS)-only, FIRST record wins
on a multi-allelic collision. REF/ALT are NOT in the key. The T4 drop keys on (CHR,POS); drop-only, NO re-key.

The occlusion manifest this consumes (from 07b occlusion_manifest.py) carries per-variant GRCh37 (chr, pos_grch37)
after Stage-B liftover. scan_present_rate populates the manifest's traits_present / n_traits_present columns.

The 63bdb59 present_rate= SEAM (src/python/occlusion_manifest.py — THIS PLAN PREDATES IT; it is now shipped code):
```python
enrich_occlusion_manifest(manifest_path, chain_path, *, out_path=None, present_rate=None) -> Path   # :320-323
```
  * `present_rate` is consumed EXACTLY as `{(chr, pos_grch37): {...}}` — GRCh37, POST-LIFTOVER (:330-331). The
    docstring itself cites `test_occlusion_present_rate_scan.py:72` (`target = (1, 5_982_778)`) as that key's
    source of truth. => **`scan_present_rate`'s return is DIRECTLY FEEDABLE to `present_rate=` — write NO adapter.**
  * It joins on `(chr, pos_grch37)` via `_present_rate_key` (:296-317, :372-374) — **NOT** on `variant_id` (the scan
    reads GRCh37 sumstats by (CHR,POS) and can never compute a GRCh38 variant_id).
  * RAISE BOUNDARY — do NOT rediscover this during integration: a non-lifting row -> `pd.NA`, never a raise;
    non-empty `present_rate` + >=1 LIFTABLE row + ZERO key matches -> **raises ValueError** (:385-388); non-empty
    `present_rate` + ZERO liftable rows -> no raise, all `pd.NA`.
  * `STAGE_B_TRAIT_COLUMNS = ["traits_present", "n_traits_present", "n_traits_scanned"]` (:103) — the RED's return
    keys ARE the manifest's column names, which is why they must match exactly.
  * 63bdb59 added 4 seam tests to `tests/m3/test_occlusion_manifest.py` (already GREEN, do not edit):
    test_present_rate_joins_on_the_chr_pos_grch37_tuple_key,
    test_present_rate_leaves_na_for_a_variant_that_did_not_lift,
    test_present_rate_matching_no_liftable_row_raises_not_silent_na,
    test_present_rate_against_a_wholly_unliftable_manifest_does_not_raise.
  * NOTE the direction of travel: this plan's prose ALREADY correctly assumed the manifest carries (chr, pos_grch37);
    63bdb59 aligned the SHIPPED CONSUMER to that assumption. **The plan's premise is now TRUE in code, not aspirational.**

The deferred m3-04 seam (src/snakemake/rules/finemap.smk:89-93): the production consume rule is
`m3-04-W4-production-and-egress-PLAN.md` = STALE / SUPERSEDED-PENDING-REPLAN (must be re-planned to consume
m3-02e's AFR-native `.npz`). Do NOT wire the filter into finemap.smk here — that is the m3-04 replan's job.

Env = /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest (py3.11, numpy/pandas, no hail).
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1 (T3): occlusion_present_rate_scan.py — genome-wide present-rate-per-ancestry scan over the 9 public AFR sumstats</name>
  <read_first>
    src/python/occlusion_present_rate_scan.py (to create), .planning/amendments/m3_region1_occlusion_hinge_check.md:124-141
    (the zcat|awk scan prototype + auto-detect CHR/POS), src/python/occlusion_manifest.py (07b T2 — consumes the rate),
    tests/m3/test_occlusion_present_rate_scan.py (RED from 07a — do NOT edit expectations).
  </read_first>
  <files>src/python/occlusion_present_rate_scan.py</files>
  <behavior>
    - **THE RED IS THE CONTRACT** (tests/m3/test_occlusion_present_rate_scan.py — do NOT edit it; match it).
      The export is `scan_present_rate` — NOT any other name:
      ```python
      scan_present_rate(variants_grch37, sumstats_paths) -> dict
      ```
    - **KEY TYPE IS LOAD-BEARING: the returned dict is keyed by the (chr:int, pos:int) GRCh37 TUPLE** — NOT a
      string, NOT a variant_id. The RED does `target = (1, 5_982_778)` then `res[target]`
      (test_occlusion_present_rate_scan.py:72,81). That same tuple is the manifest join key (see the 63bdb59 seam
      in `<interfaces>`), which is WHY it must be a tuple.
    - Each value is a per-variant dict with EXACTLY these keys (:82-84, :132):
      `{"n_traits_present": int, "n_traits_scanned": int, "present_rate": float, "traits_present": list[str]}`.
      `present_rate` == n_traits_present / n_traits_scanned (k/n). `traits_present` NAMES the traits carrying the
      variant (RED :132 asserts `sorted(res[v]["traits_present"]) == ["bmi", "sbp"]`) and feeds the manifest's
      `traits_present` column. These four names ARE `STAGE_B_TRAIT_COLUMNS` + the rate — they must match exactly.
    - For each occluded variant (already lifted to GRCh37 (CHR,POS)), does a sumstats row exist at that (CHR,POS)?
      Auto-detect CHR/POS columns from the harmonized header BY NAME (CHR POS REF ALT BETA SE P
      EAF N SNP_ID TRAIT ANCESTRY BUILD; fall back to cols 1/2). RED :139-157 REORDERS the columns and requires the
      identical rate — a POSITIONAL read scores the wrong column and fails. "per ancestry" generalizes the scan to
      each {trait}.{ANC} group (here all 9 AFR files). PUBLIC GRCh37 sumstats only, read-only
      (REQ-PUBLIC-DATA-ONLY); no perimeter, no spend. Reads .tsv.bgz via the same zcat|awk-equivalent (pandas
      chunked or subprocess zcat).
    - An ABSENT variant returns a RECORD with n_traits_present == 0 and present_rate == 0.0 (:87-101) — NOT a
      missing key, NOT a ZeroDivisionError.
    - Synthetic-fixture unit: variant present in k of n files -> present_rate k/n; absent -> 0.
    - The REAL 9-file genome-wide scan is an integration/validation step (gated, out of scope for unit CI) — the
      function is unit-covered on synthetic fixtures now.
  </behavior>
  <action>
    GREEN the 07a present-rate tests. Create src/python/occlusion_present_rate_scan.py with
    scan_present_rate(...) as above, reusing the hinge-check auto-detect-CHR/POS scan logic. Keep it a pure,
    deterministic function over file paths so it is CI-runnable on tiny synthetic TSV fixtures (plain TSV or .bgz).
    Output a per-variant present-rate table (the metric that sizes the Angle-1/3 scientific cost). Commit GREEN,
    explicit paths, tag m3-07c-W7-T3.
  </action>
  <acceptance_criteria>
    - `pytest tests/m3/test_occlusion_present_rate_scan.py -x` exits 0 (k/n present-rate on synthetic fixtures; absent -> 0; CHR/POS auto-detected).
    - `grep -c "present_rate" src/python/occlusion_present_rate_scan.py` >= 1.
    - `git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` is EMPTY.
  </acceptance_criteria>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_occlusion_present_rate_scan.py -x -q</automated>
  </verify>
  <done>scan_present_rate reports PRESENT-vs-ABSENT k/n per occluded variant over public GRCh37 AFR sumstats (auto-detected CHR/POS BY NAME), returning {n_traits_present, n_traits_scanned, present_rate, traits_present} keyed by the (chr:int, pos:int) GRCh37 tuple — directly feedable to enrich_occlusion_manifest(present_rate=...); unit-covered on synthetic fixtures; frozen files byte-unchanged.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2 (T4): drop_occluded_from_sumstats.py — reusable lockstep (CHR,POS) drop-only filter (m3-04 wiring DEFERRED)</name>
  <read_first>
    src/python/drop_occluded_from_sumstats.py (to create), src/R/regularization/snp_id_bridge.R:107-121 ((CHR,POS)
    membership, first-wins collision), src/snakemake/rules/finemap.smk:89-93 (m3-04-W4 STALE/SUPERSEDED-PENDING-REPLAN
    — the wiring seam is DEFERRED), src/python/occlusion_manifest.py (the manifest this consumes),
    tests/m3/test_occlusion_lockstep_drop.py (RED from 07a — do NOT edit expectations),
    .planning/amendments/m3_region1_occlusion_hinge_check.md (rs182965575 present 7/9 — the orphan this prevents).
  </read_first>
  <files>src/python/drop_occluded_from_sumstats.py</files>
  <behavior>
    - **THE RED IS THE CONTRACT** (tests/m3/test_occlusion_lockstep_drop.py — do NOT edit it; match it). The
      function NAME is the ONLY thing this plan previously got right; the signature, return, and logging mechanism
      were all wrong. The contract, stated in the RED's own docstring (:10) and exercised at :104/:121/:136/:196-197/:314:
      ```python
      drop_occluded_from_sumstats(sumstats_path, manifest_path, out_path) -> dict
      ```
    - **THIS IS FILE-IN / FILE-OUT — NOT DataFrame-in / tuple-out.** All THREE positional args are FILE PATHS, and
      the function WRITES `out_path`. This changes what the module IS. There is NO `build` kwarg — no such keyword
      argument exists anywhere in the RED (0 occurrences); do not add one. **An executor must NOT "adapt" the RED to a DataFrame API to make it fit this
      plan: the RED wins.** (Mirrors plink_ld_to_npz.plink_ld_to_npz's module.function path-in/path-out shape.)
    - **THE MANIFEST IS A FILE**, not an in-memory object: a TSV with columns `region_id, variant_id, chr,
      pos_grch37` (`_write_manifest` :69-80). Only `(chr, pos_grch37)` is load-bearing for the drop; `region_id` /
      `variant_id` ride along as provenance.
    - **RETURNS A COUNTS DICT** `{"n_in": int, "n_dropped": int, "n_out": int}` (:243-247), with the invariant
      `n_in - n_dropped == n_out` (:246) and `n_out` == the number of BODY ROWS ACTUALLY WRITTEN to `out_path`
      (:247 asserts `len(_body_lines(out)) == res["n_out"]`). The counts are durable so the lockstep is auditable
      against the panel's `n_dropped_occluded`.
    - Removes EXACTLY the rows whose (CHR,POS) matches a manifest entry's GRCh37 (chr, pos_grch37). Drop-only — NO
      re-key, NO allele re-orientation (snp_id_bridge.R (CHR,POS) semantics; first-wins on multi-allelic collision);
      SNP_ID is passed through untouched, never re-derived (:165-179).
    - **THE KEY IS CHR-AWARE** (:112-124): the same POS on a DIFFERENT chromosome SURVIVES. A POS-only key would
      silently delete unrelated variants genome-wide.
    - **EVERY DROP IS LOGGED TO STDERR** — provenance, not a debug nicety. The RED asserts it via
      `test_logs_each_drop(tmp_path, capsys)` (:208) reading `err = capsys.readouterr().err` (:223) and requiring
      each dropped COORDINATE to be NAMED in stderr (`str(_SNP_C_B37) in err`, `"8000000" in err`; :226-227).
      It is a STREAM WRITE, not a returned structure — the counts dict carries no log field.
    - Non-occluded rows are BYTE-IDENTICAL: header verbatim, surviving rows verbatim and IN ORDER (:160-162). A
      filter that silently reformats survivors is a re-key by another name.
    - **IDEMPOTENT — AND IDEMPOTENCE MEANS RE-RUNNING ON ITS OWN OUTPUT**, not merely "a second call changes
      nothing": the RED does `res2 = drop_occluded_from_sumstats(out1, mf, out2)` (:197) and requires
      `res2["n_dropped"] == 0` (:200) AND `out2.read_bytes() == out1.read_bytes()` (:201). **Therefore `out_path`
      must be re-readable AS INPUT** — same header, same format. This is a STRONGER contract than a no-op flag; it
      is what makes the filter survive a replay after preemption.
    - `n_dropped == 0` IS A VALID NO-OP, NOT an error (:127-139): an occluded variant with no row in this trait's
      sumstats drops nothing — present-rate k/n < 1 is the NORMAL case.
    - **THE SEAM TEST (:272-319) runs the REAL 07b producer END-TO-END** (`build_region_records` ->
      `add_grch37_positions` -> `to_csv` -> `drop_occluded_from_sumstats`) and asserts every lifted record carries
      the `chr` + `pos_grch37` drop key (:301-304), so 07b and 07c cannot each ship green while producing a manifest
      the other cannot consume. It FAILS today for the right reason (chain file present + pyliftover installed —
      MEASURED, it does NOT skip).
    - Prevents orphaning a sumstats-present occluded variant (rs182965575 present 7/9 AFR) — the reason
      panel-only-exclude is unsafe.
    - This is the REUSABLE filter (RESEARCH open-decision #3, RESOLVED). The EXACT m3-04 consume wiring
      (run_susie_rss.R sumstats-load vs a pre-fit harmonization filter vs a Snakemake rule) is DEFERRED to the m3-04
      replan — documented as an explicit seam in the module docstring, NOT wired here (finemap.smk:89-93 is STALE).
  </behavior>
  <action>
    GREEN the 07a lockstep tests. Create src/python/drop_occluded_from_sumstats.py implementing the (CHR,POS)
    drop-only filter above as FILE-IN / FILE-OUT — `drop_occluded_from_sumstats(sumstats_path, manifest_path,
    out_path) -> dict` reading both TSVs, writing `out_path`, returning `{n_in, n_dropped, n_out}`, and logging each
    dropped coordinate to STDERR (pandas or a streaming line filter; deterministic; idempotent when re-run on its own
    output). Do NOT reshape the RED into a DataFrame API. Docstring MUST state the DEFERRED wiring seam
    explicitly: "the m3-04 consume rule is SUPERSEDED-PENDING-REPLAN (finemap.smk:89-93); this reusable filter is
    wired at the sumstats-load seam when the m3-04 consume replan lands — keyed on the same manifest (CHR,POS) as the
    panel exclusion so panel and sumstats stay in lockstep (no orphaned variant)." Do NOT modify finemap.smk or any
    consume rule in this plan (that is the m3-04 replan's job). Commit GREEN, explicit paths, tag m3-07c-W7-T4.
  </action>
  <acceptance_criteria>
    - `pytest tests/m3/test_occlusion_lockstep_drop.py -x` exits 0 (drop = exactly manifest (CHR,POS); non-occluded rows byte-identical; idempotent; no re-key).
    - `grep -c "SUPERSEDED-PENDING-REPLAN\|m3-04" src/python/drop_occluded_from_sumstats.py` >= 1 (deferred seam documented).
    - `git diff --stat src/snakemake/rules/finemap.smk src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` is EMPTY (no consume wiring, no frozen-contract change).
  </acceptance_criteria>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_occlusion_lockstep_drop.py -x -q</automated>
  </verify>
  <done>Reusable manifest-driven (CHR,POS) drop-only filter GREEN as FILE-IN/FILE-OUT — drop_occluded_from_sumstats(sumstats_path, manifest_path, out_path) -> {n_in, n_dropped, n_out} with n_in - n_dropped == n_out and n_out == rows written; chr-aware; drops logged to STDERR; survivors byte-identical; no re-key; no orphan; idempotent when re-run on its OWN OUTPUT (n_dropped == 0, byte-identical); the producer->consumer seam test composes with the real 07b manifest; the m3-04 consume wiring is a documented deferred seam (finemap.smk untouched); frozen files byte-unchanged.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| public GRCh37 AFR sumstats → present-rate scan | Read-only scan over already-public sumstats; no perimeter data, no individual-level data (REQ-PUBLIC-DATA-ONLY). |
| panel ↔ sumstats join ((CHR,POS)) | Excluding a panel record (07b) without a lockstep sumstats drop orphans a sumstats-present variant (rs182965575 present 7/9 AFR) — the desync boundary T4 closes. |
| occlusion manifest → sumstats filter | The manifest's GRCh37 (CHR,POS) drives the drop; a wrong key would drop the wrong variant — keyed identically to the panel exclusion (07b). |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-m3-07c-01 | Tampering / integrity | panel↔sumstats desync (orphaned variant) | mitigate | Lockstep drop (T4) keyed on the SAME manifest (CHR,POS) as the 07b panel exclusion; drop-only, no re-key; idempotent; prevents orphaning rs182965575. |
| T-m3-07c-02 | Information disclosure | present-rate scan / lockstep filter | mitigate | Both run NC-State on already-PUBLIC GRCh37 sumstats (REQ-PUBLIC-DATA-ONLY); no perimeter, no genotypes, no per-person counts. |
| T-m3-07c-03 | Tampering | wrong (CHR,POS) drop | mitigate | Drop keyed on the manifest's lifted GRCh37 (CHR,POS); unit tests pin drop = exactly the manifest set, non-occluded rows byte-identical, idempotent. |
</threat_model>

<verification>
- Task 1 (T3): `pytest tests/m3/test_occlusion_present_rate_scan.py -x` all green (k/n on synthetic sumstats).
- Task 2 (T4): `pytest tests/m3/test_occlusion_lockstep_drop.py -x` all green (exact (CHR,POS) drop, idempotent, no re-key); finemap.smk untouched.
- Plan-scoped regression: `pytest tests/m3 -k "present_rate or lockstep" -q` green. (The 07b span-filter/manifest suites remain green from 07b.)
- Frozen-contract gate: `git diff --stat src/snakemake/rules/finemap.smk src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` EMPTY; m3-06 condition_ld_matrix.py NOT touched.
- NO perimeter access, NO loop contact, NO re-fire. The real 9-file genome-wide present-rate scan is a gated integration step; unit-covered on synthetic fixtures now.
</verification>

<success_criteria>
- The present-rate scan quantifies PRESENT-vs-ABSENT per occluded variant over public GRCh37 AFR sumstats (REQ-PUBLIC-DATA-ONLY, REQ-AOU-LD-VALIDATION).
- The reusable lockstep (CHR,POS) drop-only filter exists + is tested (idempotent, no re-key, no orphan); the m3-04 consume wiring is a documented deferred seam (finemap.smk untouched).
- Frozen contracts + m3-06 condition_ld_matrix.py are byte-unchanged (NaN→0 stays dead).
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-07c-W7-present-rate-and-lockstep-SUMMARY.md`.
Record: the present-rate scan design + the synthetic-fixture unit result; the lockstep drop (exact/idempotent/no-orphan);
the DEFERRED m3-04 consume-wiring seam (finemap.smk untouched); and the frozen-contract git-diff-clean confirmation.
</output>

---

## plan_vs_red_reconciliation — 2026-07-16 (quick 260716-0lj, DOCS-ONLY, pre-execution)

> **Everything BELOW this heading is the reconciliation record, not spec.** It deliberately QUOTES the
> old drifted identifiers so the drift is auditable; they must appear NOWHERE above this line.
> Mirrors `f3b79fe`, which did exactly this for the 07b plan pre-execution.

**PRECEDENCE — settled by m3-07b, do NOT re-litigate: THE TESTS ARE THE CONTRACT.** 07b's SUMMARY:
"Manifest API follows the TESTS' names …; the plan's prose names differ and are provided as aliases.
Tests are the contract." This pass therefore **fixed THIS PLAN and left the RED untouched (0-line diff:
`git diff --stat 13a2e6c..HEAD -- src/ tests/` is EMPTY)**. m3-07c is **NOT started** — it needs Carter's
explicit GO. The 15 RED failures still stand: 6 in `test_occlusion_present_rate_scan.py` (missing module
`occlusion_present_rate_scan`, T3) + 9 in `test_occlusion_lockstep_drop.py` (missing module
`drop_occluded_from_sumstats`, T4).

### ⚠ THE STALE CLAIM THIS RETIRES

The 2026-07-15 handoff asserted: *"07c's plan was CHECKED for the drift that hit 07b's plan — it has none."*
**That claim was STALE AND WRONG — BOTH tasks had drifted.** Do not trust it again; this note supersedes it.

**HOW T4 SLIPPED THROUGH: the check was NAME-ONLY.** `drop_occluded_from_sumstats` — the function NAME —
matched the RED exactly, so a name-grep passed it clean. Its *signature*, *return*, *logging mechanism*, and
a phantom `build=` kwarg **all** contradicted the RED. A name-only check cannot see shape drift.
**Lesson (generalizes past 07c): grep the NAME, then read the ASSERTIONS.**

### T3 drift — FIXED (6 sites: `:20, :27, :96, :117, :129, :142`)

Against `tests/m3/test_occlusion_present_rate_scan.py`. The plan was **self-contradictory**: `:96` already used
the RED's real column names while `:117` spec'd a return shape that appears NOWHERE in the RED.

| concern         | plan said (WRONG)           | RED requires (AUTHORITATIVE) — now spec'd |
|-----------------|-----------------------------|-------------------------------------------|
| function name   | `present_rate_for_variants` | `scan_present_rate` (:79)                 |
| numerator key   | `present_count`             | `n_traits_present` (:82)                  |
| denominator key | `scanned_count`             | `n_traits_scanned` (:83)                  |
| trait-list key  | `files_present`             | `traits_present` (:132)                   |

Also now stated explicitly (was absent, and is load-bearing): the return is **keyed by the `(chr:int, pos:int)`
GRCh37 TUPLE** — `target = (1, 5_982_778)`; `res[target]` (:72, :81). **6 sites, not the 4 predicted.**

### T4 drift — FIXED (4 sites: `:21, :156, :158, :160`)

Against `tests/m3/test_occlusion_lockstep_drop.py`. **The NAME matched — nothing else did.**

| concern   | plan said (WRONG)                         | RED requires (AUTHORITATIVE) — now spec'd        |
|-----------|-------------------------------------------|--------------------------------------------------|
| params    | `(sumstats_df, manifest, build='GRCh37')` | `(sumstats_path, manifest_path, out_path)` (:10) |
| shape     | DataFrame-in / tuple-out                  | **FILE-IN / FILE-OUT** — writes `out_path` (:104)|
| return    | `(filtered_df, drop_log)`                 | a **dict**: `n_in` / `n_dropped` / `n_out` (:243-247) |
| logging   | `drop_log` records each drop              | **STDERR** — `capsys.readouterr().err` (:208,:223,:226-227) |
| `build=`  | `build='GRCh37'` kwarg                    | **no such kwarg exists** (0 occurrences)         |

Grep-confirmed **0 occurrences** in the RED of: `sumstats_df`, `filtered_df`, `drop_log`, `build=`.
**4 sites, not the 2 predicted.** Two further corrections beyond the rename — the RED is *stronger* than the
old prose, so paraphrasing it away would have lost real contract:
* **idempotence** was "a second application is a no-op (`drop_log` empty)". The RED re-runs the filter **on its
  own OUTPUT** — `drop_occluded_from_sumstats(out1, mf, out2)` (:197) — requiring `n_dropped == 0` (:200) AND
  `out2.read_bytes() == out1.read_bytes()` (:201). **The output must be re-readable AS INPUT.** Strictly stronger.
* **the manifest is a FILE** (TSV: `region_id, variant_id, chr, pos_grch37`; only `(chr, pos_grch37)` load-bearing),
  not an in-memory object — which is what makes the whole signature file-in/file-out.

**T4 is RECONCILED IN THIS PASS — not deferred, no open flag.**

### The 63bdb59 seam this plan predated — now recorded in `<interfaces>`

`enrich_occlusion_manifest(present_rate=...)` consumes EXACTLY `{(chr, pos_grch37): {...}}`, joins **POST-lift** on
`(chr, pos_grch37)` (NOT `variant_id`), and **raises ValueError** if liftable keys exist but none match. So
`scan_present_rate`'s return is **directly feedable — no adapter**, and the raise boundary need not be rediscovered
during integration. Note the direction: the plan's `:95-96` **already** correctly assumed `(chr, pos_grch37)`;
63bdb59 aligned the shipped consumer to it. **The plan's premise is now TRUE in code, not aspirational.**

### Scope of this pass

DOCS-ONLY, one file. **The SCIENCE and SCOPE are UNCHANGED**: T3 still scans the 9 public GRCh37 AFR harmonized
sumstats (CHR/POS auto-detected BY NAME); T4 is still the reusable (CHR,POS) drop-only lockstep filter (no re-key,
no orphan — rs182965575 present 7/9 AFR); the m3-04 consume-wiring remains a DISCLOSED deferral
(`finemap.smk` m3-04-W4 STALE/SUPERSEDED-PENDING-REPLAN). Tasks not renumbered; threat_model untouched.
REQ-PUBLIC-DATA-ONLY — no perimeter, no spend, no loop contact. Checked against the RED **POST-63bdb59**.

**Why this mattered:** the plan is the executor's PROMPT. A drifted spec is an unsatisfiable instruction whose
likeliest escape is the executor **editing the tests** to match — corrupting the contract by proxy. That is the
failure [[feedback_check_plan_against_red_before_executing]] exists to prevent, and it is why T4's
file-in/file-out identity is now called out in bold rather than merely renamed.
