---
phase: m3-aou-afr-ld-panel-build
plan: 04
type: execute
wave: 4
depends_on: ["00", "02", "03"]
files_modified:
  - src/snakemake/rules/m3_validation.smk
  - src/python/validate_bundle_sizes.py
  - data/processed/ld_reference/AFR_aou/.touch_prod
  - data/processed/ld_reference/EUR_aou/.touch_prod
  - .planning/amendments/aou-egress-audit-log.md
  - .planning/amendments/sha256/.gitkeep
autonomous: false
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "AOU-2 production fire executes against config/ld_regions.tsv (322 rows; full union × 2 ancestries) gated on m3_dev_complete.flag (Wave 2 deliverable). Cluster-hours: ~160-260 per RESEARCH cost analysis (D-M3-02)."
    - "Pre-egress validate_bundle_sizes.py per-chromosome × ancestry verifies no bundle exceeds 50 GB compressed; if any bundle > 50 GB, splits within-chromosome by region count (e.g., chr1a + chr1b) per RESEARCH Q4."
    - "Per-chromosome × ancestry egress requests filed at AoU portal (44 total: 22 chr × 2 ancestries). Each request gets an AoU-issued export request ID."
    - "Per-bundle .npz files (and BlockMatrix-shard directories for Path A.3 regions) gsutil cp'd from AoU bucket to data/interim/aou_ld_exports/{AFR_aou,EUR_aou}/."
    - "Per-bundle row appended to .planning/amendments/aou-egress-audit-log.md with Q12 schema: timestamp, chr, ancestry, n_regions, compressed size, AoU export request ID, OSF cross-ref, SHA-256 manifest path."
    - "Per-bundle SHA-256 manifest sub-file lands at .planning/amendments/sha256/m3_chr{N}_{ANCESTRY}_aou.tsv (44 small files)."
    - "m3_convert_npz_rds.smk fires per region (Wave 3 rules) on the production bundles; data/processed/ld_reference/AFR_aou/{region_id}.rds (161 files) + EUR_aou/{region_id}.rds (161 files) land; .npz files deleted post-conversion per AOU-LD-PIPELINE.md §10.3 size budget."
    - "Wave 2 4-check protocol re-runs at sample-30-region scale on production fire via m3_validation.smk to catch systemic-bug regressions between dev and production scale."
    - "Toy-3-locus pipeline (REQ-SNAKEMAKE-CI) is extended at Wave 5 — NOT this wave; here we just verify the resolver chain works end-to-end on a real region."
  artifacts:
    - path: "src/snakemake/rules/m3_validation.smk"
      provides: "Production-scale 4-check sample validation rules (Check 4 yield contrast on random 30-region sample)"
    - path: "src/python/validate_bundle_sizes.py"
      provides: "Per-chromosome bundle size estimator + within-chromosome splitter (Q4 50 GB cap enforcement)"
    - path: "data/processed/ld_reference/AFR_aou/{region_id}.rds"
      provides: "161 production AFR LD .rds files"
    - path: "data/processed/ld_reference/EUR_aou/{region_id}.rds"
      provides: "161 production EUR LD .rds files"
    - path: ".planning/amendments/aou-egress-audit-log.md"
      provides: "Per-bundle audit-log rows (44 incremental appends as bundles arrive)"
      contains: "Per-Bundle Audit Entries"
    - path: ".planning/amendments/sha256/"
      provides: "44 per-bundle SHA-256 manifest sub-files"
  key_links:
    - from: ".planning/notebooks/AOU-2_per_region_ld.ipynb"
      to: "config/ld_regions.tsv"
      via: "USE_DEV_SUBSET=False — Wave 4 production toggle"
      pattern: "USE_DEV_SUBSET = False"
    - from: "src/snakemake/rules/m3_convert_npz_rds.smk"
      to: "m3_dev_complete.flag"
      via: "Production rule input includes the dev-complete gate"
      pattern: "m3_dev_complete.flag"
    - from: ".planning/amendments/aou-egress-audit-log.md"
      to: ".planning/amendments/sha256/m3_chr{N}_{ANCESTRY}_aou.tsv"
      via: "SHA-256 manifest path column in each audit-log row"
      pattern: "sha256/m3_chr"
---

<objective>
Wave 4 fires the 322-cell production LD panel inside AoU (160-260 cluster-hours per RESEARCH §11; ~3-5 days wall clock with 8-12 concurrent Dataproc jobs at AoU's quota ceiling), files the 44 per-chromosome × ancestry egress requests, lands the .npz files on NCSU GPFS, runs Wave 3's converter to produce 322 .rds files, samples a 30-region Check 4 yield-contrast at production scale, and appends 44 per-bundle audit-log rows.

Purpose: The actual production deliverable. Carter pre-condition: m3_dev_complete.flag exists (Wave 2 signoff). Without that flag, the Snakemake DAG refuses to fire any Wave 4 production rule. Each of the 44 egress requests is a Carter human action — we cannot pre-batch them in code; AoU portal review SLA is 2-5 business days per request.

Output: 322 production .rds files, 44 audit-log rows, 44 SHA-256 sub-manifests, a 30-region production-scale Check 4 sample report.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION.md
@.planning/amendments/AOU-LD-PIPELINE.md

<interfaces>
<!-- Wave 0-3 deliverables Wave 4 consumes. -->

config/ld_regions.tsv (Wave 0; 322 rows × 12 cols)
config/ld_regions_dev.tsv (Wave 0; 10 rows; production fire ignores)
m3_dev_complete.flag (Wave 2 deliverable; required input for Wave 4 Snakemake production rules)

src/snakemake/rules/m3_convert_npz_rds.smk (Wave 3):
- rule build_ld_rds_aou_afr — input data/interim/aou_ld_exports/AFR_aou/{region_id}.npz; output data/processed/ld_reference/AFR_aou/{region_id}.rds
- rule build_ld_rds_aou_eur — same for EUR

src/snakemake/rules/m3_ingest_aou_ld.smk (Wave 3):
- rule m3_ingest_aou_export_arrives — flag-driven gate per (ancestry, chr) bundle

.planning/notebooks/AOU-2_per_region_ld.ipynb (Wave 2):
- USE_DEV_SUBSET = True — Wave 2 dev fire
- USE_DEV_SUBSET = False — Wave 4 production fire

RESEARCH Q4 per-chromosome bundle sizes (estimated):
- AFR total ~250-400 GB across 22 chr (median 12-19 GB per chr)
- EUR total ~400-700 GB across 22 chr (median 18-30 GB per chr)
- 50 GB cap per RESEARCH Q4 mitigation: split chr1 if needed

Q12 audit log row schema:
| Timestamp | Phase | Chr | Ancestry | n_regions | Compressed size (GB) | AoU export request ID | OSF cross-ref | SHA-256 manifest path | Bundle content (region_ids) | Reviewed by AoU on | Egressed to NCSU on | Notes |
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Pre-egress bundle-size validator + m3_validation.smk production-scale sample harness</name>
  <files>src/python/validate_bundle_sizes.py, src/snakemake/rules/m3_validation.smk, Snakefile</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "Q4 — Per-chromosome export bundle size estimate" (lines 201-235) — verbatim 50 GB cap + within-chromosome split logic
    - src/snakemake/rules/m3_convert_npz_rds.smk (Wave 3) — Wave 4 fires the production rules with m3_dev_complete.flag gating
    - src/snakemake/rules/m3_ingest_aou_ld.smk (Wave 3) — flag pattern this validation harness wraps
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "Validation Architecture > Check 4" (lines 546-550) — production-scale Check 4 sampling strategy
  </read_first>
  <action>
    1. Write `src/python/validate_bundle_sizes.py` (~80 lines):
       ```python
       """Pre-egress bundle-size validator. Checks per-chromosome × ancestry .npz bundles
       in the AoU workspace bucket against the 50 GB compressed cap (RESEARCH Q4). If any
       bundle > 50 GB, emits a within-chromosome split plan (e.g., chr1 → chr1a + chr1b).

       Run from inside AoU workspace OR on NCSU side after `gsutil du -h gs://...` output capture.
       """
       import argparse, json, sys, pandas as pd
       BUNDLE_CAP_GB = 50

       def main():
           p = argparse.ArgumentParser()
           p.add_argument("--bundle-sizes-tsv", required=True,
                          help="TSV with columns: ancestry, chr, region_id, compressed_size_bytes")
           p.add_argument("--out-plan", required=True,
                          help="Output bundle plan TSV: ancestry, chr, sub_bundle, region_ids, total_size_gb")
           args = p.parse_args()
           sizes = pd.read_csv(args.bundle_sizes_tsv, sep="\t")
           plan_rows = []
           for (ancestry, chr_), grp in sizes.groupby(["ancestry", "chr"]):
               grp = grp.sort_values("region_id")
               total_gb = grp["compressed_size_bytes"].sum() / 1024**3
               if total_gb <= BUNDLE_CAP_GB:
                   plan_rows.append({"ancestry": ancestry, "chr": chr_, "sub_bundle": f"chr{chr_}",
                                     "region_ids": ",".join(grp["region_id"].tolist()),
                                     "total_size_gb": round(total_gb, 2)})
                   continue
               # Split: round-robin until each sub-bundle < 50 GB
               sub = "a"; cur_size = 0; cur_regions = []
               for _, row in grp.iterrows():
                   region_gb = row["compressed_size_bytes"] / 1024**3
                   if cur_size + region_gb > BUNDLE_CAP_GB and cur_regions:
                       plan_rows.append({"ancestry": ancestry, "chr": chr_,
                                         "sub_bundle": f"chr{chr_}{sub}",
                                         "region_ids": ",".join(cur_regions),
                                         "total_size_gb": round(cur_size, 2)})
                       sub = chr(ord(sub) + 1); cur_size = 0; cur_regions = []
                   cur_size += region_gb; cur_regions.append(row["region_id"])
               if cur_regions:
                   plan_rows.append({"ancestry": ancestry, "chr": chr_,
                                     "sub_bundle": f"chr{chr_}{sub}",
                                     "region_ids": ",".join(cur_regions),
                                     "total_size_gb": round(cur_size, 2)})
           plan = pd.DataFrame(plan_rows)
           plan.to_csv(args.out_plan, sep="\t", index=False)
           print(f"WROTE {args.out_plan} ({len(plan)} bundles)")
           return 0

       if __name__ == "__main__":
           sys.exit(main())
       ```

    2. Write `src/snakemake/rules/m3_validation.smk` (~80 lines). Three rules:
       ```python
       from pathlib import Path
       M3_R_LD_ENV = str(Path(workflow.basedir) / "envs" / "m3-r-ld.yml")
       LD_REF_DIR = config["paths"]["ld_reference"]
       VALIDATION_DIR = ".planning/phases/m3-aou-afr-ld-panel-build/validation"

       rule m3_validation_check_4_production_sample:
           """Production-scale Check 4 yield-contrast sample on 30 random AFR regions.
           Gated on m3_dev_complete.flag (Wave 2). Catches systemic-bug regressions.
           """
           input:
               flag = "m3_dev_complete.flag",
               manifest = "config/ld_regions.tsv",
               afr_rds = expand(os.path.join(LD_REF_DIR, "AFR_aou", "{region_id}.rds"),
                                region_id=config.get("m3_validation_sample_region_ids", [])),
           output:
               yield_table = os.path.join(VALIDATION_DIR, "production_check_4_sample.tsv"),
           log:
               "logs/m3_validation/check_4_production_sample.log",
           conda:
               M3_R_LD_ENV
           shell:
               "Rscript src/scripts/m3_check_4_production_sample.R {input.manifest} {input.flag} {output.yield_table} &> {log}"

       rule m3_validation_complete:
           """Phase-gate: only complete after the production-scale Check 4 sample passes."""
           input:
               sample_table = rules.m3_validation_check_4_production_sample.output.yield_table,
           output:
               flag = "m3_validation_complete.flag",
           shell:
               "touch {output.flag}"
       ```

    3. Update top-level `Snakefile` to include the new rule file:
       ```python
       include: "src/snakemake/rules/m3_validation.smk"
       ```
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; python -c "
import pandas as pd, subprocess, tempfile, os
# Synthetic bundle-size TSV
with tempfile.NamedTemporaryFile(suffix='.tsv', mode='w', delete=False) as fin:
  fin.write('ancestry\tchr\tregion_id\tcompressed_size_bytes\n')
  for chr_ in [1,2]:
    for r in range(20):
      fin.write(f'AFR_aou\t{chr_}\tm2_region_{chr_:02d}{r:03d}\t{3*1024**3}\n')
  in_path=fin.name
out_path=in_path.replace('.tsv','_plan.tsv')
subprocess.run(['python','src/python/validate_bundle_sizes.py','--bundle-sizes-tsv',in_path,'--out-plan',out_path],check=True)
plan=pd.read_csv(out_path,sep='\t')
print(plan)
assert (plan['total_size_gb'] &lt;= 50.0).all(), 'bundle plan exceeded 50 GB cap'
print('OK')
" &amp;&amp; grep -c "include:.*m3_validation.smk" Snakefile</automated>
  </verify>
  <acceptance_criteria>
    - `wc -l src/python/validate_bundle_sizes.py` returns ≥ 50.
    - `grep -c "BUNDLE_CAP_GB = 50" src/python/validate_bundle_sizes.py` returns 1.
    - `grep -c "rule m3_validation_check_4_production_sample" src/snakemake/rules/m3_validation.smk` returns 1.
    - `grep -c "rule m3_validation_complete" src/snakemake/rules/m3_validation.smk` returns 1.
    - `grep -c "m3_dev_complete.flag" src/snakemake/rules/m3_validation.smk` returns ≥ 1 (production gate).
    - `grep -c "include:.*m3_validation.smk" Snakefile` returns 1.
    - Inline synthetic-bundle test passes (validate_bundle_sizes.py produces a plan TSV with all sub-bundles ≤ 50 GB).
    - `snakemake --snakefile Snakefile --dry-run --use-conda m3_validation_complete.flag` exits 0.
  </acceptance_criteria>
  <done>
    Bundle-size validator + production-scale Check 4 sample harness land. The validation rule explicitly gates on m3_dev_complete.flag, enforcing D-M3-03 single-fire-after-dev order in code (not just policy).
  </done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 2: Production fire 322 cells (AoU Dataproc) + 44 per-chromosome egress requests + 44 audit-log rows</name>
  <files>data/processed/ld_reference/AFR_aou/.touch_prod, data/processed/ld_reference/EUR_aou/.touch_prod, .planning/amendments/aou-egress-audit-log.md, .planning/amendments/sha256/.gitkeep</files>
  <read_first>
    - .planning/notebooks/AOU-2_per_region_ld.ipynb (Wave 2; flip USE_DEV_SUBSET to False)
    - src/snakemake/rules/m3_convert_npz_rds.smk (Wave 3 rules; will fire per region as bundles arrive)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "Q4" (lines 201-235; per-chromosome bundle size estimates) AND "Q12" (lines 445-481; audit-log row schema)
    - .planning/amendments/aou-egress-audit-log.md (Wave 0 seed + Wave 1 ruling row)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md (Wave 2 deliverable; D-M3-09 ruling already accepted)
  </read_first>
  <action>See &lt;human_gate&gt; block. This task is a Carter human-action checkpoint; no agent action. The agent's role is to verify acceptance_criteria after Carter completes the gate.</action>
  <human_gate>
    <gate>Production fire 322 cells + 44 per-chromosome egress requests</gate>
    <description>
      THE production deliverable. Carter human-action stack:

      Step A — Production fire (single Dataproc job batch; 3-5 days wall clock):
      1. Open AoU workspace; mirror updated AOU-2 notebook with USE_DEV_SUBSET = False.
      2. Submit 8-12 concurrent Dataproc jobs at AoU's quota ceiling per RESEARCH §11 cost-lever recommendations (preemptible secondary workers for ~60% low-density regions).
      3. Each job processes a chunk of ~30-40 regions; total ~160-260 cluster-hours per RESEARCH §11.
      4. Path A.3 regions (>10 Mb; ~92 of 322 per Wave 0 region-class projection) emit BlockMatrix-shard directories at gs://${WORKSPACE_BUCKET}/ld/{ANCESTRY}_aou/bm/{region_id}.bm/ — Carter gsutil cp's these along with the .npz files at egress time.
      5. Job-completion log captured at gs://${WORKSPACE_BUCKET}/ld/ld_run_log_prod.tsv.

      Step B — Per-chromosome bundle inventory (1 hour):
      1. Run validate_bundle_sizes.py on the production bundle inventory (gsutil du -h output).
      2. Output: bundle plan with up to 44 sub-bundles (most chromosomes ≤ 50 GB; chr1, chr2, possibly chr12 may need within-chromosome split per RESEARCH Q4).

      Step C — File 44 (or up to 50 if splits needed) AoU egress requests (multi-week wall clock):
      1. Per chromosome × ancestry, file an AoU portal Notebooks/Files egress request with descriptive label "M3 LD chr{N} {ANCESTRY}_aou".
      2. AoU SLA: 2-5 business days per request (44 × 3 days median = ~3 months calendar if sequential; if parallelizable, ~3-4 weeks).
      3. As each AoU export approval arrives: gsutil cp the bundle from AoU bucket to data/interim/aou_ld_exports/{ANCESTRY}_aou/.
      4. As each .npz file lands on NCSU: Snakemake auto-fires Wave 3 m3_convert_npz_rds.smk rules (per region) to produce .rds at data/processed/ld_reference/{ANCESTRY}_aou/{region_id}.rds. The conversion happens per-region as bundles arrive — incrementally builds the production panel.
      5. Per-bundle: emit .planning/amendments/sha256/m3_chr{N}_{ANCESTRY}_aou.tsv with one SHA-256 row per .npz file (use sha256sum data/interim/aou_ld_exports/{ANCESTRY}_aou/m2_region_*.npz).
      6. Per-bundle: append a row to .planning/amendments/aou-egress-audit-log.md per Q12 schema with: ISO-8601 timestamp, phase=M3, chr, ancestry, n_regions, compressed_size_GB, AoU export request ID, OSF cross-ref=osf.io/az52u, SHA-256 manifest path, bundle content (comma-list of region_ids), AoU review date, NCSU egress date, notes (Path A.1/A.2/A.3 distribution for the bundle).
      7. Commit each bundle audit log update with token (m3-W4-T2-chr{N}-{ANCESTRY}) for granular audit trail.

      Step D — Production-scale validation sample (1-2 days):
      1. After all 44 bundles arrive AND all 322 .rds files land: run `snakemake --use-conda m3_validation_complete.flag`.
      2. Inspect production_check_4_sample.tsv — should show consistent yield-contrast direction with Wave 2 dev fire.
      3. If anomalies: halt, diagnose, document in m3-VALIDATION-MEMO.md "Production-scale validation" addendum.

      Touch placeholder files data/processed/ld_reference/AFR_aou/.touch_prod and data/processed/ld_reference/EUR_aou/.touch_prod once 161+161 .rds files have all landed (these mark wave completion).
    </description>
    <unblocks>Wave 5 (close-out) + downstream M2-supplementary phase + M4 fine-mapping</unblocks>
    <how-to-resolve>
      1. Fire production AoU compute (Step A; ~3-5 days wall clock; ~$5-10k AoU credit consumption per RESEARCH §11).
      2. Run validate_bundle_sizes.py (Step B).
      3. File 44 (or up to 50) egress requests + gsutil cp + audit-log appends (Step C; ~3-4 weeks calendar; ~30 minutes per bundle Carter time).
      4. Run snakemake m3_validation_complete (Step D).
      5. After all 4 steps: type "approved" — Wave 5 unblocked.
      6. If any AoU egress rejects (R1 fallback): halt + escalate; M3 may need partial-panel fallback or in-AoU SuSiE path.
    </how-to-resolve>
  </human_gate>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; ls data/processed/ld_reference/AFR_aou/*.rds 2&gt;/dev/null | wc -l &amp;&amp; ls data/processed/ld_reference/EUR_aou/*.rds 2&gt;/dev/null | wc -l &amp;&amp; grep -cE "^\\| 2026-[0-9]{2}-[0-9]{2}T" .planning/amendments/aou-egress-audit-log.md &amp;&amp; ls .planning/amendments/sha256/m3_chr*.tsv 2&gt;/dev/null | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - `ls data/processed/ld_reference/AFR_aou/*.rds | wc -l` returns 161 (one .rds per AFR region).
    - `ls data/processed/ld_reference/EUR_aou/*.rds | wc -l` returns 161 (one .rds per EUR region).
    - `grep -cE "^\\| 2026-[0-9]{2}-[0-9]{2}T" .planning/amendments/aou-egress-audit-log.md` returns ≥ 44 (per-bundle rows; up to 50 if splits needed).
    - `ls .planning/amendments/sha256/m3_chr*.tsv | wc -l` returns ≥ 44.
    - `test -f data/processed/ld_reference/AFR_aou/.touch_prod && test -f data/processed/ld_reference/EUR_aou/.touch_prod` exits 0.
    - `snakemake --snakefile Snakefile --use-conda m3_validation_complete.flag` exits 0 AND `test -f m3_validation_complete.flag` exits 0.
    - `grep -c "AoU-EXPORT-" .planning/amendments/aou-egress-audit-log.md` returns ≥ 44 (each row carries an AoU-issued export request ID).
    - `wc -l .planning/amendments/sha256/m3_chr1_AFR_aou.tsv` returns ≥ 6 (a chr1 bundle should have ≥ 6 regions per RESEARCH Q4 14-region chr1 estimate; conservative).
    - Per-region .rds size on disk: `find data/processed/ld_reference/AFR_aou/ -name "*.rds" -size +0` returns 161 lines (all non-empty).
    - Git log shows ≥ 44 commits with `(m3-W4-T2-chr` prefix in the subject.
  </acceptance_criteria>
  <done>
    322 .rds files land on GPFS. 44+ per-bundle audit-log rows committed (one per chromosome × ancestry). 44+ SHA-256 sub-manifests committed. m3_validation_complete.flag touched. M2-supplementary phase + M4 are now unblocked (consume {AFR_aou,EUR_aou}/*.rds via the ld_panel: resolver chain).
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| AoU bucket ↔ NCSU GPFS | The 44-bundle production egress crossing. EVERY crossing carries an AoU-issued export request ID + classification ruling cross-ref + SHA-256 manifest. This is the highest-volume boundary in the project. |
| GPFS .rds files ↔ M4 fine-mapping consumers | Wave 5 + M2-supplementary phase + M4 read these .rds files via the ld_panel: resolver chain. Provenance JSON inside each .rds anchors auditability. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M3-EGR-W4 | Information disclosure | 44-bundle production egress | mitigate | (a) AoU egress classification ruling (Wave 1 R1 hard gate) governs every bundle. (b) Per-bundle audit log row records: timestamp, AoU export request ID, n_regions, compressed size, SHA-256 manifest path. (c) bundle size validator caps each bundle at 50 GB compressed (RESEARCH Q4) — within AoU's typical reviewer tolerance. (d) per-bundle SHA-256 manifest sub-files (44 of them under .planning/amendments/sha256/) provide byte-for-byte reproducibility for Zenodo deposit at publication. |
| T-M3-S2-W4 | Reproducibility / provenance | 322 .rds production artifacts | mitigate | Each .rds carries a `provenance` field (Wave 3 converter output) with chain SHA + datetime + n_var counts. Per-region commit token (m3-W4-T2-chr{N}-{ANCESTRY}) provides per-bundle git-level audit. |
| T-M3-S1-W4 | Tampering / supply chain | bundle-size validator | accept | validate_bundle_sizes.py is pure-Python (pandas only); deterministic; runs locally. |
| T-M3-AUTH-W4 | Authorization | m3_validation.smk production gate | mitigate | Snakemake DAG enforces m3_dev_complete.flag as input to m3_validation_check_4_production_sample. Carter cannot bypass without manually editing the rule file (auditable in git). |
| T-M3-EGR-AUDIT-W4 | Information disclosure | 44 per-bundle audit log rows | mitigate | append-only convention (.gitattributes merge=union recommended); commit-token discipline; OSF cross-reference column ties every row to osf.io/az52u for external auditability. |
</threat_model>

<verification>
**Wave 4 phase-level checks:**

1. `ls data/processed/ld_reference/AFR_aou/*.rds | wc -l` returns 161.
2. `ls data/processed/ld_reference/EUR_aou/*.rds | wc -l` returns 161.
3. `grep -cE "^\\| 2026-[0-9]{2}-[0-9]{2}T" .planning/amendments/aou-egress-audit-log.md` ≥ 44.
4. `ls .planning/amendments/sha256/m3_chr*.tsv | wc -l` ≥ 44.
5. `test -f m3_validation_complete.flag` exits 0.
6. `pytest tests/m3 -x` passes (no regression from Wave 3 + earlier).
7. `snakemake --snakefile Snakefile --dry-run --use-conda data/processed/ld_reference/AFR_aou/m2_region_00067.rds` exits 0 with "Nothing to be done" (file already exists).
</verification>

<success_criteria>
- 322 production .rds files land on GPFS under data/processed/ld_reference/{AFR_aou,EUR_aou}/.
- 44+ per-bundle audit-log rows committed with AoU export request IDs + SHA-256 manifest paths + Q12 schema.
- 44+ SHA-256 sub-manifests under .planning/amendments/sha256/.
- m3_validation_complete.flag touched (production-scale Check 4 sample passed).
- Wave 5 close-out is unblocked.
- M2-supplementary phase + M4 fine-mapping have working AoU LD panels available via ld_panel: resolver.
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-04-W4-production-and-egress-SUMMARY.md` recording:
- Cluster-hours actually used (vs ~160-260 estimate)
- Per-bundle compressed size distribution
- Path A.1/A.2/A.3 region count per ancestry
- AoU credit balance after production
- Egress timing (calendar days first to last bundle)
- Any region-failures (e.g., regions whose Hail compute failed; Path B PLINK fallbacks)
- Production-scale Check 4 sample yield-contrast outcome (consistency vs Wave 2 dev)
</output>
