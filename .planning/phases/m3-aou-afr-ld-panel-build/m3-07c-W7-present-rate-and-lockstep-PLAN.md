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
    - "occlusion_present_rate_scan.present_rate_for_variants reports PRESENT-vs-ABSENT rate per occluded variant (k/n) over the 9 public GRCh37 AFR harmonized sumstats (header CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD), auto-detecting CHR/POS cols — REQ-PUBLIC-DATA-ONLY (no perimeter, read-only). Unit-covered on synthetic fixtures; the real 9-file scan is a gated integration step."
    - "drop_occluded_from_sumstats(sumstats_df, manifest, build='GRCh37') removes EXACTLY the manifest's GRCh37 (CHR,POS) rows (drop-only, no re-key — snp_id_bridge.R (CHR,POS) semantics), logs each drop, leaves non-occluded rows byte-identical, and is IDEMPOTENT (2nd apply = no-op); prevents orphaning a sumstats-present occluded variant (rs182965575 present 7/9 AFR)."
    - "The exact m3-04 consume-step wiring is a DOCUMENTED deferred hook (finemap.smk:89-93 STALE/SUPERSEDED-PENDING-REPLAN): the reusable filter lands NOW with tests; the wiring is deferred to the m3-04 replan (RESEARCH open-decision #3, checker-approved) — finemap.smk is NOT modified here."
    - "Frozen contracts stay byte-unchanged: `git diff --stat src/snakemake/rules/finemap.smk src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` is EMPTY — no consume wiring, no frozen-contract change; m3-06 condition_ld_matrix.py is NOT touched."
  artifacts:
    - path: "src/python/occlusion_present_rate_scan.py"
      provides: "Genome-wide present-rate-per-ancestry scan of occluded variants over the 9 AFR harmonized GRCh37 sumstats"
      exports: ["present_rate_for_variants"]
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
after Stage-B liftover. present_rate_for_variants populates the manifest's traits_present / n_traits_present columns.

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
    - present_rate_for_variants(variants_grch37, sumstats_paths) -> per-variant {present_count, scanned_count,
      present_rate, files_present}. For each occluded variant (already lifted to GRCh37 (CHR,POS)), does a sumstats
      row exist at that (CHR,POS)? Auto-detect CHR/POS columns from the harmonized header (CHR POS REF ALT BETA SE P
      EAF N SNP_ID TRAIT ANCESTRY BUILD; fall back to cols 1/2). "per ancestry" generalizes the scan to each
      {trait}.{ANC} group (here all 9 AFR files). PUBLIC GRCh37 sumstats only, read-only (REQ-PUBLIC-DATA-ONLY);
      no perimeter, no spend. Reads .tsv.bgz via the same zcat|awk-equivalent (pandas chunked or subprocess zcat).
    - Synthetic-fixture unit: variant present in k of n files -> present_rate k/n; absent -> 0.
    - The REAL 9-file genome-wide scan is an integration/validation step (gated, out of scope for unit CI) — the
      function is unit-covered on synthetic fixtures now.
  </behavior>
  <action>
    GREEN the 07a present-rate tests. Create src/python/occlusion_present_rate_scan.py with
    present_rate_for_variants(...) as above, reusing the hinge-check auto-detect-CHR/POS scan logic. Keep it a pure,
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
  <done>present_rate_for_variants reports PRESENT-vs-ABSENT k/n per occluded variant over public GRCh37 AFR sumstats (auto-detected CHR/POS); unit-covered on synthetic fixtures; frozen files byte-unchanged.</done>
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
    - drop_occluded_from_sumstats(sumstats_df, manifest, build="GRCh37") -> (filtered_df, drop_log). Removes EXACTLY
      the rows whose (CHR,POS) matches a manifest entry's GRCh37 (chr, pos_grch37). Drop-only — NO re-key, NO allele
      re-orientation (snp_id_bridge.R (CHR,POS) semantics; first-wins on multi-allelic collision). drop_log records
      each dropped (chr,pos,variant_id,reason). Non-occluded rows are byte-identical (same order, same values).
      IDEMPOTENT: a second application is a no-op (drop_log empty). Prevents orphaning a sumstats-present occluded
      variant (rs182965575 present 7/9 AFR) — the reason panel-only-exclude is unsafe.
    - This is the REUSABLE filter (RESEARCH open-decision #3, RESOLVED). The EXACT m3-04 consume wiring
      (run_susie_rss.R sumstats-load vs a pre-fit harmonization filter vs a Snakemake rule) is DEFERRED to the m3-04
      replan — documented as an explicit seam in the module docstring, NOT wired here (finemap.smk:89-93 is STALE).
  </behavior>
  <action>
    GREEN the 07a lockstep tests. Create src/python/drop_occluded_from_sumstats.py implementing the (CHR,POS)
    drop-only filter above (pandas; deterministic; idempotent). Docstring MUST state the DEFERRED wiring seam
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
  <done>Reusable manifest-driven (CHR,POS) drop-only filter GREEN (idempotent, no re-key, no orphan); the m3-04 consume wiring is a documented deferred seam (finemap.smk untouched); frozen files byte-unchanged.</done>
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
