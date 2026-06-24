---
phase: m3-aou-afr-ld-panel-build
plan: 02e
type: execute
# W-1 (plan-checker): wave is 4, NOT 2 -- m3-02e genuinely depends_on m3-03 (wave 3:
# the resolver, ld_npz_to_rds.R, m3_convert_npz_rds.smk it consumes). A wave-2 plan
# cannot depend on a wave-3 plan. The "02e / W2-re-scope-series" id is HISTORICAL
# naming (the m3-02b/02c/02d/02e cost-re-scope lineage), decoupled here from the
# execution wave. Execution-ordering truth = wave: 4.
wave: 4
depends_on: ["02b", "02d", "03"]
supersedes_note: "m3-02e RETIRES the Hail BlockMatrix LD-panel build for BOTH ancestries. m3-04-W4-production-and-egress-PLAN.md (the 322-cell Hail LD production fire) is SUPERSEDED-PENDING-REPLAN: it must be re-planned to CONSUME the m3-02e AFR-native .npz + the public EUR .rds, NOT to rebuild LD via Hail (160-260 cluster-h). See Task 3 + the objective."
files_modified:
  - src/python/aou_ld_panel.py
  - src/python/plink_ld_to_npz.py
  - src/python/build_public_eur_manifest.py
  - src/snakemake/scripts/download_ukbb_ld_tiles.py
  - src/snakemake/scripts/ukbb_ld_tile_to_region_rds.py
  - src/snakemake/rules/m3_public_eur_ld.smk
  - src/snakemake/rules/m3_convert_npz_rds.smk
  - src/snakemake/rules/finemap.smk
  - config/pipeline.yaml
  - Snakefile
  - tests/m3/test_plink_ld_to_npz.py
  - tests/m3/test_public_eur_manifest.py
  - tests/m3/test_ld_panel_resolver.py
  - tests/m3/test_finemap_loader_contract.py
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-02e-AFR-NATIVE-FIRE-BRIEF.md
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-native-plink-panel.tsv
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-02e-cluster-shutdown.md
autonomous: false
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION
  - REQ-PUBLIC-DATA-ONLY
  - REQ-PATH-PARAMETERIZATION
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "MOVE 1 (AFR LD in-house but NATIVE, NOT Hail BlockMatrix): a new src/python/plink_ld_to_npz.py reader converts a native plink1.9 per-region LD output (square `.ld.bin` float32 OR banded `.ld.gz`) PLUS its `.bim` (variant order) PLUS an allele-frequency sidecar into the SAME egress-clean `.npz` contract the downstream loader already consumes (keys: ld, variant_ids, rsids, allele_freq, lower_triangular). The PILOT-recommended default is SQUARE bin4 (SuSiE-ready, fixed-size, verified symmetric); BANDED with an r2 floor is a documented disk-tight alternate. The square path writes lower_triangular=False; the banded path writes lower_triangular=True (it materializes one triangle). The lower_triangular flag is set CORRECTLY for each mode (feedback_npz_triangle_flag_contract — getting it wrong silently halves or doubles off-diagonals, which bit the project twice: CR-01 doubling + BR-01 A.3 halving)."
    - "The in-perimeter EXPORT step is added to src/python/aou_ld_panel.py as a NATIVE-path helper (export the QC'd AFR cohort ONCE from the Hail MT to plink .bed/.bim/.fam via hl.export_plink, one count_cols scan amortized across all regions), and a per-region plink LD driver spec (the exact `plink1.9 --bfile <cohort> --keep-allele-order --extract-range/--chr/--from-bp/--to-bp --r square bin4` invocation per AFR compute window). --keep-allele-order is MANDATORY on EVERY plink LD call (else LD signs mismatch GWAS z-scores -> susieR failure); a test asserts the emitted command string contains --keep-allele-order. This REPLACES the Hail BlockMatrix A.3 path for the AFR panel (the ~34k-cluster-h / ~17k-cluster-h-AFR-half path is NOT taken; m3-02d's ordering-B A.3 write stays in the tree as the retired Hail path but is no longer the AFR route)."
    - "MOVE 2 (EUR LD = PUBLIC reference, $0 compute): the existing Weissbrod/PolyFun UKBB-LD scaffold (src/snakemake/scripts/download_ukbb_ld_tiles.py + ukbb_ld_tile_to_region_rds.py + the EUR_ukbb chain entry + the broad-alkesgroup-ukbb-ld bucket config) is EXTENDED to ingest the public UKBB 337k EUR LD panel as the M3 EUR source, with a hg19->hg38 coordinate adapter so the public reference's variants reconcile against the GRCh38-native AFR panel and the GRCh37-canonical analytic plane (DEC-2026-04-24-01). PRIMARY = Weissbrod/PolyFun UKBB 337k (.npz, 3 Mb regions, CC-BY no-sign-request, hg19); Pan-UKBB 420k is a DOCUMENTED ALTERNATE recorded in the manifest builder. A new src/python/build_public_eur_manifest.py maps each M2 EUR region to the overlapping public-panel tile(s) and emits the per-region extract jobs; the resulting EUR `.rds` drops into the same downstream loader contract as the AFR `.npz`->`.rds`. The public panel is fetched via AWS S3 (boto3 UNSIGNED anonymous) from s3://broad-alkesgroup-ukbb-ld/ — NOT GCS — so the download rule uses the S3/boto3 env (envs/ld_build.yml), the same env the existing download_ukbb_ld_tiles rule uses."
    - "config/pipeline.yaml ld_panel: EUR chain head is the public UKBB panel for M3 (a new `EUR_ukbb_pub` source pointing at data/processed/ld_reference/EUR_ukbb_pub/{region_safe}.rds), placed AHEAD of the legacy EUR_aou / EUR_ukbb / EUR_1kg entries; the resolver resolves a representative EUR region to the public panel. AFR chain head stays AFR_aou (the native-plink .npz->.rds). A resolver test asserts the EUR public source is the chain head and the AFR head is unchanged."
    - "MOVE 3 (downstream on NCSU): the finemap resolver + the .npz->.rds ingest path are wired so coloc/SuSiE consume the AFR-native `.npz` and the public EUR `.rds` through ONE loader contract; the SuSiE-RSS estimate_s (z-vs-LD consistency) diagnostic is wired as a per-region guard on the loaded LD (Zou 2022 — guards allele-flip/encoding mismatch between the LD source and the GWAS z-scores, the exact failure --keep-allele-order and the public-EUR liftover are most exposed to). THIS plan scopes Move 3 to the resolver + loader + estimate_s-guard changes the two NEW LD sources require. BOUNDARY (B-1, corrected): the AFR LD PANEL itself (the ~276 per-ancestry AFR compute windows) is BUILT by THIS plan's in-perimeter native-plink fire (Task 4) + the public EUR LD is built $0 in Task 2 — so the LD-build is COMPLETE within m3-02e. m3-04-W4-production-and-egress-PLAN.md is the STALE 322-cell HAIL LD-panel production fire (322 = the pre-m3-02d 161 union regions x 2 ancestries; the post-m3-02d per-ancestry count is 276 AFR + EUR windows) and is now SUPERSEDED-PENDING-REPLAN: it must be re-planned to CONSUME m3-02e's AFR-native .npz + public EUR .rds, NOT to rebuild LD via Hail. The downstream coloc/SuSiE FINE-MAPPING fire (an M4 concern) is unaffected. Task 3 records this supersede explicitly."
    - "EGRESS DISCIPLINE (REQ-AOU-LD-EGRESS): only the aggregate per-region LD matrix (variant x variant r) + AF leaves the AoU perimeter; never individual-level genotypes. The AFR LD .npz is egress-clean per the prior G0 ruling (aou-egress-audit-log.md). The plink .bed/.bim/.fam cohort export stays IN-PERIMETER (it is individual-level) and is consumed only by the in-perimeter plink LD loop; the export bed never crosses egress. A code comment + the fire brief both state this boundary."
    - "PILOT CAVEATS folded into the budget commitment: the in-perimeter fire brief re-measures the PRODUCTION-VM wall (the pilot's $4.19/$1.49 rates are labelled n2-highmem-64 but the pilot ran on n2-standard-16 -> the per-region wall is re-measured on the actual production VM before the full 276-region loop commits budget); the banded ~400M-pair count is flagged as ESTIMATED-from-size (exact wc -l deferred to the fire); per-region export is ~33s with the count_cols scan paid ONCE (~20 min). The fire brief carries the GREEN pilot numbers (square 56.224 min/region -> 258.6 VM-h -> $385 Spot / $1,084 on-demand x276) as the going-in budget with the re-measure-before-commit gate."
    - "THE IN-PERIMETER FIRE (autonomous:false, Carter fires; the ONLY billable task): export the QC'd AFR cohort once to plink .bed, then loop the ~276 AFR compute windows on a single Spot VM running plink1.9 --r square bin4 --keep-allele-order, producing a per-region square float32 LD + AF sidecar, then run plink_ld_to_npz.py per region to land the egress-clean .npz, data-layer-verify each (gsutil du + a numpy shape/symmetry/diag==1 read-back; _SUCCESS / file-existence is NOT evidence per D-M3-10), bundle per-chromosome under the egress ceiling (reuse ld_egress_bundle.py from m3-02d), egress, and shut the VM down with a verified shutdown artifact. Token-free handback (AoU cat's the panel TSV + shutdown record; NCSU reconstructs + pushes — NO Workbench push token; feedback_push_ncsu_before_aou_clone_fire). The panel TSV m3-W2-native-plink-panel.tsv records per-region wall/RAM/output-size/n_var so the real production cost is measured, not extrapolated from one pilot cell."
    - "All NON-fire tasks are autonomous NCSU code+test (TDD RED-first; smoke_dev py3.11 env which has pandas — the m3-r-ld env does not). Reused utilities are NOT duplicated: the .npz contract + lower_triangular flag (aou_ld_panel.py _save_npz / bm_to_npz.py), the manifest reader + _normalize_bucket (aou_ld_panel.py), the liftover converter (ld_npz_to_rds.R), the per-chrom egress bundler (ld_egress_bundle.py), and the UKBB tile extractor (download_ukbb_ld_tiles.py / ukbb_ld_tile_to_region_rds.py) are EXTENDED, not re-implemented."
  artifacts:
    - path: "src/python/plink_ld_to_npz.py"
      provides: "Native-plink LD reader: square `.ld.bin` OR banded `.ld.gz` + `.bim` + AF sidecar -> egress-clean .npz with the CORRECT lower_triangular flag per mode"
      min_lines: 90
    - path: "src/python/aou_ld_panel.py"
      provides: "export_cohort_to_plink() (hl.export_plink, one count_cols scan amortized) + build_plink_ld_command() (per-region --r square bin4 --keep-allele-order, MANDATORY allele-order flag)"
      contains: "keep-allele-order"
    - path: "src/python/build_public_eur_manifest.py"
      provides: "Map each M2 EUR region to overlapping public UKBB 337k tile(s); emit per-region extract jobs; Pan-UKBB 420k recorded as documented alternate; hg19<->hg38 coordinate adapter"
      min_lines: 60
    - path: "src/snakemake/scripts/download_ukbb_ld_tiles.py"
      provides: "Extended to target the public 337k EUR panel as the M3 EUR_ukbb_pub source (build-aware: hg19 tiles)"
    - path: "src/snakemake/rules/m3_public_eur_ld.smk"
      provides: "Snakemake rules building data/processed/ld_reference/EUR_ukbb_pub/{region_safe}.rds from the public UKBB panel; $0 compute"
    - path: "src/snakemake/rules/finemap.smk"
      provides: "estimate_s z-vs-LD consistency guard wired on the loaded LD for the two new sources"
      contains: "estimate_s"
    - path: "config/pipeline.yaml"
      provides: "EUR chain head = EUR_ukbb_pub (public 337k) ahead of EUR_aou/EUR_ukbb/EUR_1kg; AFR head stays AFR_aou (native plink)"
      contains: "EUR_ukbb_pub"
    - path: "tests/m3/test_plink_ld_to_npz.py"
      provides: "square+banded -> .npz round-trip; lower_triangular flag correct per mode; symmetry/diag==1; AF row-alignment; the .bim variant-order contract"
      min_lines: 60
    - path: "tests/m3/test_public_eur_manifest.py"
      provides: "region->tile mapping; hg19<->hg38 coordinate adapter; Pan-UKBB alternate recorded; primary=Weissbrod 337k"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-02e-AFR-NATIVE-FIRE-BRIEF.md"
      provides: "Turnkey in-perimeter runbook: export-once -> plink loop -> .npz -> verify -> egress -> shutdown -> token-free handback; re-measure-production-VM-wall gate; PILOT going-in numbers"
      min_lines: 80
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-native-plink-panel.tsv"
      provides: "Per-region wall/RAM/output-size/n_var from the fire (REPLACES the one-cell pilot TSV as the real production-cost measurement; written by the handback)"
      contains: "wall_min"
  key_links:
    - from: "src/python/aou_ld_panel.py::build_plink_ld_command"
      to: "the per-region plink1.9 --r invocation"
      via: "--keep-allele-order is always present (sign-correct LD for susieR)"
      pattern: "keep-allele-order"
    - from: "src/python/plink_ld_to_npz.py"
      to: "the egress-clean .npz (ld/variant_ids/rsids/allele_freq/lower_triangular)"
      via: "square->lower_triangular=False, banded->lower_triangular=True (correct flag per mode)"
      pattern: "lower_triangular"
    - from: "config/pipeline.yaml ld_panel.EUR"
      to: "data/processed/ld_reference/EUR_ukbb_pub/{region_safe}.rds"
      via: "EUR_ukbb_pub is the chain head ahead of the legacy entries"
      pattern: "EUR_ukbb_pub"
    - from: "src/snakemake/rules/finemap.smk"
      to: "the loaded LD matrix"
      via: "estimate_s z-vs-LD consistency guard (Zou 2022)"
      pattern: "estimate_s"
    - from: "src/python/plink_ld_to_npz.py"
      to: "ld_npz_to_rds.R (the existing loader/liftover/provenance converter)"
      via: "same .npz contract -> no R-side change needed"
      pattern: "savez_compressed"
---

<objective>
Re-architect Wave 2's LD build around the GREEN native-plink PILOT (m3-W2-pilot-report.md, 2026-06-24) and the accepted 3-move cost design (m3-W2-cost-effective-rearchitecture.md). The Hail BlockMatrix path (~34k cluster-h projected, ~17k for the AFR half, NOT-GREEN at any plausible cap) is NOT taken. Instead:

- **Move 1 — AFR LD in-house but NATIVE.** Export the QC'd AFR cohort ONCE from the Hail MT to plink `.bed/.bim/.fam` (one-time count_cols scan amortized), then compute per-region LD on a single Spot VM looping the ~276 AFR compute windows with native `plink1.9 --r square bin4 --keep-allele-order`, landing a square float32 LD + AF sidecar per region. A new NCSU reader converts the plink output to the SAME egress-clean `.npz` contract the downstream loader already consumes. The pilot measured 56.224 min/region square on an n2-standard-16 -> 258.6 VM-h x276 -> ~$385 Spot / $1,084 on-demand: GREEN, ~1-2 OOM cheaper than Hail's ~24 cluster-h for the SAME cell.

- **Move 2 — EUR LD = PUBLIC reference ($0 compute).** Extend the existing Weissbrod/PolyFun UKBB-LD scaffold (download_ukbb_ld_tiles.py + ukbb_ld_tile_to_region_rds.py + the EUR_ukbb chain + the broad-alkesgroup-ukbb-ld bucket config already in the tree) to ingest the public UKBB 337k EUR LD panel as the M3 EUR source, with a hg19<->hg38 coordinate adapter. PRIMARY = Weissbrod/PolyFun 337k; Pan-UKBB 420k is a documented alternate. The public panel is closer to in-sample for a UKB-based EUR GWAS than AoU's 220k would be (MultiSuSiE/SuSiEx precedent: a matched public reference per ancestry).

- **Move 3 — downstream on NCSU.** Wire the resolver + loader so coloc/SuSiE consume AFR-native `.npz` + public EUR `.rds` through one contract, with the SuSiE-RSS `estimate_s` z-vs-LD diagnostic as a per-region guard (Zou 2022 — guards exactly the allele-flip/encoding mismatch that --keep-allele-order and the public-EUR liftover are most exposed to). The ~276-window AFR LD panel build is THIS plan's in-perimeter task (Task 4) and the public EUR LD is built $0 (Task 2) — the M3 LD-build is complete within m3-02e. m3-04 (the stale 322-cell HAIL LD production fire; 322 = pre-m3-02d 161x2, 276 = post-m3-02d per-ancestry count) is SUPERSEDED-PENDING-REPLAN — it must consume m3-02e's outputs, not rebuild LD via Hail. Downstream coloc/SuSiE fine-mapping is an M4 concern, unaffected.

This plan delivers FOUR autonomous NCSU code+test artifacts (the plink->npz reader, the export/command helpers in aou_ld_panel, the public-EUR manifest+ingest, the resolver+estimate_s wiring) and ONE in-perimeter fire (autonomous:false; Carter fires) that exports the AFR cohort once, runs the native plink LD loop over 276 regions, lands the egress-clean .npz panel, and refreshes the cost measurement with REAL per-region production-VM walls.

Purpose: build the AFR LD panel at ~1-2 OOM lower cost than the Hail path, get EUR LD for $0 from a better-matched public reference, and keep all downstream on NCSU — delivering the full M3 LD substrate inside the $3-4k budget per the GREEN pilot.

Output: plink_ld_to_npz.py + the export/command helpers + the public-EUR manifest/rules + the resolver/estimate_s wiring + their tests, the turnkey AFR-native fire brief, and (from the fire) the real-cost native-plink panel TSV + the verified shutdown artifact.

LOCKED (do NOT relitigate):
- AFR LD = native plink1.9 on a single Spot VM (PILOT-validated). LDstore2 / emeraLD are alternates only. The Hail BlockMatrix path is NOT taken.
- EUR LD = PUBLIC UKBB reference, $0 compute (Carter chose public). Weissbrod/PolyFun 337k PRIMARY, Pan-UKBB 420k documented alternate.
- Output mode = square bin4 (SuSiE-ready, fixed-size, verified symmetric). Banded + r2 floor is the disk-tight documented alternate, not the default.
- --keep-allele-order is MANDATORY on every plink LD call.
- The .npz triangle-flag contract is authoritative; every producer sets lower_triangular correctly (square=False, banded=True).
- Egress: only aggregate LD + AF crosses; the plink cohort .bed stays in-perimeter.
- AoU AFR WGS stays the committed AFR substrate (feedback_no_1000g_ld_pivot); only the TOOL changes (Hail -> native plink).

D-02e DECISIONS (auto-selected defaults from the --auto invocation; logged for traceability; Carter may override any):
- D-02e-01 (auto-selected default, Carter may override): OUTPUT MODE = square bin4. Rationale: PILOT recommendation — SuSiE-ready, fixed-size, random-access, verified symmetric (sym_check=0.0). Banded `.ld.gz` + r2 floor is the documented disk-tight alternate (~4.2 TB vs ~4.6 TB square across 276 regions). plink_ld_to_npz.py supports BOTH; the default and the fire brief use square.
- D-02e-02 (auto-selected default, Carter may override): EUR REFERENCE = Weissbrod/PolyFun UKBB 337k `.npz` as PRIMARY (format closest to our pipeline, 3 Mb regions, CC-BY no-sign-request, hg19). Pan-UKBB 420k is the documented ALTERNATE recorded in build_public_eur_manifest.py. Liftover/coordinate-match planned against hg38.
- D-02e-03 (auto-selected default, Carter may override): NATIVE TOOL = plink1.9 (PILOT-validated v1.90b7.2). LDstore2 / emeraLD recorded as alternates only (no implementation).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-effective-rearchitecture.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-W2-pilot-report.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-W2-pilot-plink-native.tsv
@.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md
@.planning/HANDOFF.json
@.claude/skills/aou-ld-pipeline/SKILL.md

<interfaces>
<!-- Concrete contracts extracted from the source the executor will modify. -->

src/python/aou_ld_panel.py (EXISTING, 2982 lines):
- read_final_cohort_mt(uri) (line ~1205): gates-then-reads the QC'd MT (calls _final_is_trustworthy
  before `import hail`). The NATIVE export helper reads the AFR cohort via this.
- _save_npz(region_id, ld_np, variant_ids, rsids, out_bucket, out_local_dir, lower_triangular=False,
  allele_freq=None) (line ~2854): the egress-clean .npz contract. Keys written:
  ld, variant_ids, rsids, allele_freq, lower_triangular=np.array([lower_triangular]).
  *** plink_ld_to_npz.py MUST emit the EXACT same keys (so ld_npz_to_rds.R needs NO change). ***
  Asserts ld_np.dtype==float32, allele_freq present + row-aligned.
- compute_region_ld(region_row, mt_source, ...) (line ~2361): the Hail per-region driver
  (A.1/A.2/A.3 routing). The native path does NOT replace this function in-place; it ADDS
  export_cohort_to_plink() + build_plink_ld_command() as the native AFR route, and the
  fire brief drives the plink loop OUTSIDE compute_region_ld.
- _write_a3_banded_correlation_bm (line ~2743, m3-02d ordering B): the Hail A.3 write. STAYS in
  the tree as the RETIRED Hail path; the AFR panel no longer routes through it. Do NOT delete.
- Manifest reader + _normalize_bucket + WORKSPACE_BUCKET pin conventions are in this module — reuse.

config/ld_regions.tsv (EXISTING, post-m3-02d, per-ancestry buffer AFR 3Mb / EUR 5Mb):
- 276 AFR rows (123 __sub compute windows + whole rows) and 276 EUR rows.
- Columns include: region_id, chr, start_grch38, end_grch38, ancestry, parent_region_id,
  subregion_index, n_subregions, core_start_grch38, core_end_grch38, window_start_grch38,
  window_end_grch38, buffer_bp, radius_bp, region_class.
- *** The AFR plink loop iterates the AFR rows' window_start_grch38..window_end_grch38 (GRCh38,
  AoU-native) — plink --chr/--from-bp/--to-bp extract per window. ***

src/python/plink_ld_to_npz.py (NEW — sibling of bm_to_npz.py):
- The bm_to_npz.py convention to mirror: _load_sidecar/_load_af_sidecar, the n_rows length guards,
  np.tril for banded storage, lower_triangular=np.array([True/False]), float32 cast.
- Square `.ld.bin` = plink `--r square bin4` raw float32, numpy shape (n_var, n_var); read with
  np.fromfile(dtype=float32).reshape(n_var, n_var); lower_triangular=False (full matrix). Verify
  diag==1, symmetric (matches the pilot's sym_check=0.0).
- Banded `.ld.gz` = plink `--r gz` columns CHR_A BP_A SNP_A CHR_B BP_B SNP_B R; scatter the signed R
  into a sparse/triangle array; lower_triangular=True (one populated triangle).
- variant order from the cohort `.bim` (plink writes LD in .bim row order; --keep-allele-order keeps
  A1/A2 == GWAS allele order). *** CANONICAL VID RESOLVED (W-3): the project canonical
  variant id is `chr:pos:REF:ALT` = `str(locus) + ":" + alleles[0] + ":" + alleles[1]`
  (aou_ld_panel.py:2504, the vid struct in compute_region_ld). Under hl.export_plink the
  .bim convention is A1 = alt = alleles[1] and A2 = ref = alleles[0]; the .bim columns are
  [chr, rsid, cm, bp, A1, A2]. So the reconstructed vid MUST be `{chr}:{bp}:{A2}:{A1}`
  (REF=A2, ALT=A1) — NOT chr:pos:A1:A2 and NOT a bare chr:pos:A2:A1 without the REF/ALT
  semantics. Getting REF/ALT swapped silently misaligns every variant id against the .npz
  the AFR Hail path would have produced. *** rsids from .bim col 2 (or '' when '.').

src/snakemake/scripts/download_ukbb_ld_tiles.py (EXISTING, Weissbrod 2020 UKBB-LD):
- BUCKET/PREFIX point at broad-alkesgroup-ukbb-ld; Tile(chrom,start,end,npz_key); list_tiles,
  load_ld_matrix(npz_path), load_variant_tsv (cols rsid, chromosome, position, allele1, allele2),
  safe_region_id, sha256_file. *** This is the public 337k panel scaffold — Move 2 extends it. ***
- These tiles are hg19/GRCh37 (the Weissbrod build). The hg19<->hg38 adapter reconciles against
  the GRCh38-native AFR panel + the GRCh37 analytic plane (DEC-2026-04-24-01).
src/snakemake/scripts/ukbb_ld_tile_to_region_rds.py (EXISTING): single-tile region extractor;
  writes {out-dir}/{safe_region_id}.rds + .meta.json into data/processed/ld_reference/EUR_ukbb_ld.

src/python/ld_panel.py::resolve_ld_path (EXISTING, line 23): walks config['ld_panel'][ancestry]
  fallback chain; substitutes {region_id} (AoU heads) + {region_safe} (1kg/ukbb tails); honors pin +
  strict_aou_only. *** Move 3 adds EUR_ukbb_pub as the EUR chain head. ***
config/pipeline.yaml ld_panel: (EXISTING, lines ~207-228): EUR chain = [EUR_aou, EUR_ukbb, EUR_1kg];
  AFR chain = [AFR_aou, AFR_hgdp, AFR_1kg]; TRANS; strict_aou_only:false; pin:{EUR/AFR/TRANS:null}.

src/scripts/ld_npz_to_rds.R (EXISTING, 248 lines): reads the .npz (ld/variant_ids/rsids/allele_freq/
  lower_triangular), HONORS lower_triangular (TRUE -> mirror one triangle; FALSE/absent -> already-
  full, symmetrize only), GRCh38->GRCh37 pyliftover, provenance JSON (chain SHA). *** Because
  plink_ld_to_npz.py emits the IDENTICAL .npz contract, this R converter needs NO change. ***

src/python/ld_egress_bundle.py (EXISTING, m3-02d): plan_egress_bundles(cell_sizes) groups by chrom,
  splits a >EGRESS_CAP_GB(=50) chrom bundle into chrN_a/chrN_b. *** Reuse for the AFR egress step. ***

src/snakemake/rules/m3_convert_npz_rds.smk (EXISTING): build_ld_rds_aou_afr / build_ld_rds_aou_eur
  rules (npz -> Rscript ld_npz_to_rds.R -> rds). The AFR rule already consumes data/interim/
  aou_ld_exports/AFR_aou/{region_id}.npz — the native .npz lands there unchanged.

src/snakemake/rules/finemap.smk: run_finemap rule; ld_matrix input resolves via resolve_ld_path
  (wired in m3-03). Move 3 adds the estimate_s guard on the loaded LD.

PILOT going-in numbers (m3-W2-pilot-report.md, GREEN, 2026-06-24):
- Cell m2_region_00040__sub00 AFR, chr12 GRCh38 37,463,740-45,398,515 (~7.93 Mb), buffer 3Mb,
  MAF>=0.005, n_var=64,060, count_cols=73,122.
- plink1.9 v1.90b7.2, master n2-standard-16 (16 vCPU/64GB), single-node:
  square --r square bin4 --keep-allele-order: wall 56.224 min, peak RAM 17.89 GiB, .ld.bin 15.29 GiB
  (64060^2 float32, diag=1.0, symmetric sym_check=0.0).
  banded --r gz (ldwin 3000kb, r2 0): wall 25.446 min, peak RAM 16.68 GiB, .ld.gz 16.55 GiB
  (~400M pairs ESTIMATED from size).
  export_plink call 0.555 min; full export run 20m15s dominated by the ONE-TIME count_cols scan.
- x276 regions: square 258.6 VM-h ($385 Spot / $1,084 on-demand); banded 117.05 VM-h ($174/$490).
- CAVEAT: $4.19/$1.49 rates labelled n2-highmem-64 but pilot ran on n2-standard-16 -> re-measure
  the production-VM wall before committing the budget.

Live coordinates (SKILL.md / HANDOFF.json):
- Workspace aou-rw-476cdac2 . project wb-perky-corn-6639 . bucket gs://rw-migration-aou-rw-476cdac2
- Run branch m3-W2-aou-deltas (NOT main). AFR cohort MT: gs://.../ld/mt_afr_qc.mt, 73,122 samples,
  COMPLETE_VERIFIED. Cohort path is /ld/ (NOT /ld/mt/) — readers read URIs literally.
- For the EXPORT-once + plink loop the agent uses a Spot VM (Move 1) OR the existing HAIL cluster
  20260604 master for the hl.export_plink step then a Spot VM for the plink loop — the brief picks
  the cheapest valid path and re-measures the production-VM wall.
- D-M3-10: every artifact contents-validated (gsutil du + numpy/Hail read-back); _SUCCESS / mere
  file existence is NOT evidence.
- Tests run in smoke_dev py3.11 (PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH);
  it has pandas + numpy. The m3-r-ld env does NOT have pandas — do NOT target it for pytest.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1 (m3-02e-T1, autonomous): plink_ld_to_npz.py native-plink LD reader (square + banded -> the egress-clean .npz contract, correct lower_triangular per mode) + export_cohort_to_plink() + build_plink_ld_command() helpers in aou_ld_panel.py (--keep-allele-order mandatory) + tests</name>
  <files>src/python/plink_ld_to_npz.py, src/python/aou_ld_panel.py, tests/m3/test_plink_ld_to_npz.py</files>
  <read_first>
    - src/python/bm_to_npz.py (FULL — the sibling convention: _load_sidecar/_load_af_sidecar at lines 57-98, the n_rows length guards, np.tril banded storage at ~195, lower_triangular=np.array([True]) at ~205, the float32 cast, the AF-SIDECAR-01 all-NaN-with-warning fallback)
    - src/python/aou_ld_panel.py lines 2854-2913 (_save_npz — the EXACT .npz contract plink_ld_to_npz.py must match) + lines 1205-1320 (read_final_cohort_mt — how the cohort MT is gated-read) + the WORKSPACE_BUCKET/_normalize_bucket conventions
    - src/python/aou_ld_panel.py lines 2361-2540 (compute_region_ld — the Hail driver the native path runs ALONGSIDE, not inside; note _save_npz is called at ~2538 with lower_triangular + allele_freq)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-pilot-report.md (the exact plink invocations + the verified square output shape/diag/symmetry)
    - config/ld_regions.tsv (the AFR rows' window columns the plink loop extracts; header + 3 AFR __sub rows)
    - tests/m3/test_aou_ld_panel_local.py (existing test patterns + the lower_triangular flag-contract tests to NOT break)
  </read_first>
  <behavior>
    - test_plink_square_bin_to_npz: write a synthetic plink `--r square bin4` output (a 40x40 symmetric float32 raw binary, diag=1.0) + a synthetic `.bim` (40 rows: chr, rsid, cm, bp, A1, A2) + an AF sidecar (40 floats); run plink_ld_to_npz.py square mode; assert the .npz has ld shape (40,40), dtype float32, diag==1.0, symmetric, lower_triangular==False, variant_ids/rsids row-aligned to the .bim, allele_freq row-aligned. The matrix round-trips byte-equal (square is full, no triangle loss).
    - test_plink_banded_gz_to_npz: write a synthetic plink `--r gz` output (CHR_A BP_A SNP_A CHR_B BP_B SNP_B R rows, in-band pairs only) + .bim + AF; run banded mode; assert ld carries the signed R in ONE triangle, lower_triangular==True, off-band entries are 0, and ld_npz_to_rds.R's reconstruction (tri + t(tri) - diag) would recover the full matrix (assert in Python: tri + tri.T - diag(diag) == expected).
    - test_lower_triangular_flag_correct_per_mode: square -> lower_triangular==False; banded -> lower_triangular==True. A regression that flips either FAILS (feedback_npz_triangle_flag_contract: square-as-True would mirror an already-full matrix and DOUBLE off-diagonals; banded-as-False would symmetrize a one-sided matrix and HALVE them).
    - test_npz_keys_match_save_npz_contract: the .npz keys are EXACTLY {ld, variant_ids, rsids, allele_freq, lower_triangular} (the same set aou_ld_panel._save_npz / bm_to_npz write), so ld_npz_to_rds.R ingests it with NO change.
    - test_af_sidecar_row_alignment: a length-mismatched AF sidecar raises a loud ValueError (mirror the bm_to_npz n_rows guard); an OMITTED AF sidecar writes all-NaN + a warning (do NOT silently ship a wrong AF).
    - test_bim_variant_order_preserved: variant_ids/rsids come from the .bim in row order (plink writes LD in .bim order); a shuffled .bim produces correspondingly-ordered ids.
    - test_canonical_vid_reconstruction_exact (W-3, HARD TEST — the silent-misalignment vector): write a synthetic .bim row whose A1/A2 follow hl.export_plink's convention (A1=ALT=alleles[1], A2=REF=alleles[0]), e.g. .bim line `12  rs1558902  0  53809247  A  T` (A1=A, A2=T). Assert load_bim reconstructs the EXACT canonical vid `12:53809247:T:A` (chr:pos:REF:ALT = chr:pos:A2:A1), byte-equal to compute_region_ld's `str(locus)+":"+alleles[0]+":"+alleles[1]` at aou_ld_panel.py:2504 (REF=alleles[0]=A2, ALT=alleles[1]=A1). A reconstruction that emits `12:53809247:A:T` (REF/ALT swapped) FAILS. The hardcoded example is aligned to line 2504.
    - test_build_plink_ld_command_has_keep_allele_order: build_plink_ld_command(bfile, chrom, from_bp, to_bp, out_prefix, mode='square') returns a command list/string that CONTAINS --keep-allele-order AND --r square bin4 (square) / --r gz (banded) AND the --chr/--from-bp/--to-bp window; a mode that drops --keep-allele-order is not constructible (the flag is hardcoded into the helper, asserted present).
    - test_export_cohort_to_plink_invokes_export_plink: export_cohort_to_plink(mt_uri, out_bfile_prefix) calls hl.export_plink once on the gated-read cohort MT (mock hail); assert it does NOT re-scan count_cols per region (the scan is amortized — one call). Use a hail mock / importorskip so the test runs on NCSU without Hail.
    - test_afr_native_path_does_not_route_through_retired_a3 (factual note 2): the m3-02d ordering-B A.3 Hail write (_write_a3_banded_correlation_bm) STAYS in the tree (not deleted) but the NATIVE AFR route MUST NOT call it. Assert the native helpers (export_cohort_to_plink, build_plink_ld_command, plink_ld_to_npz) do NOT reference _write_a3_banded_correlation_bm / hl.row_correlation / hl.ld_matrix (AST/grep: the native code path never invokes the retired Hail A.3 BlockMatrix write); _write_a3_banded_correlation_bm itself remains present (its existing tests stay green).
  </behavior>
  <action>
    Create `src/python/plink_ld_to_npz.py` (NEW; sibling of bm_to_npz.py, ~120 lines):

    1. `read_square_bin(ld_bin_path, n_var) -> np.ndarray`: np.fromfile(dtype='<f4').reshape(n_var, n_var). Assert shape, diag~=1.0 (within tol), symmetric (allclose to its transpose, the pilot's sym_check=0.0). Cast float32.
    2. `read_banded_gz(ld_gz_path, bim_df) -> np.ndarray`: read the CHR_A BP_A SNP_A CHR_B BP_B SNP_B R columns; map SNP_A/SNP_B (or BP) to .bim row indices; scatter signed R into a (n_var, n_var) lower-triangle array (i>=j); diag=1.0. Return the one-sided triangle.
    3. `load_bim(bim_path) -> (variant_ids, rsids)`: parse the 6-col .bim
       [chr, rsid, cm, bp, A1, A2]. Reconstruct the EXACT project canonical vid
       `{chr}:{bp}:{REF}:{ALT}` where, per hl.export_plink's convention, REF = A2 (= alleles[0])
       and ALT = A1 (= alleles[1]) — i.e. variant_id = f"{chr}:{bp}:{A2}:{A1}". This MUST match
       compute_region_ld's vid = `str(locus)+":"+alleles[0]+":"+alleles[1]` at aou_ld_panel.py:2504
       (alleles[0]=REF=A2, alleles[1]=ALT=A1). DO NOT defer the REF/ALT order to executor judgment —
       it is fixed here: REF=A2, ALT=A1. rsids = col 2 (or '' when '.'). Row order == LD row order.
    4. `plink_ld_to_npz(*, mode, ld_path, bim_path, af_sidecar_path|None, out_npz, region_id)`: dispatch square/banded; load bim; load AF (reuse the bm_to_npz _load_af_sidecar all-NaN-with-warning fallback + length guard); set lower_triangular = (mode=='banded'); write the EXACT _save_npz key set (ld float32, variant_ids, rsids, allele_freq, lower_triangular=np.array([flag])) via np.savez_compressed. DO NOT import hail (this runs on the Spot VM / NCSU). REQ-PATH-PARAMETERIZATION: no hardcoded /share|/rs1|/gpfs_common paths.
    5. `argparse` main: --mode {square,banded} (default square per D-02e-01), --ld, --bim, --allele-freq (optional), --out-npz, --region-id, --n-var (square needs it for reshape).

    In `src/python/aou_ld_panel.py` (ADD, do not modify compute_region_ld in place):

    6. `build_plink_ld_command(bfile_prefix, chrom, from_bp, to_bp, out_prefix, mode='square', ld_window_kb=3000, r2_floor=0.0, threads=None) -> list[str]`: construct the plink1.9 command. ALWAYS include `--keep-allele-order` (hardcoded, not optional — the docstring states it is mandatory for sign-correct LD vs GWAS z, a susieR failure if dropped). square -> `--r square bin4`; banded -> `--r gz --ld-window-kb {kb} --ld-window 99999 --ld-window-r2 {r2_floor}`. Always `--chr {chrom} --from-bp {from_bp} --to-bp {to_bp} --bfile {bfile} --out {out_prefix}`. Return the arg list (for subprocess); the fire brief renders it.
    7. `export_cohort_to_plink(mt_uri, out_bfile_prefix, *, mt=None)`: gate-read the cohort MT via read_final_cohort_mt (or accept an injected mt for testing), then `hl.export_plink(mt, out_bfile_prefix)` ONCE. Log count_cols ONCE (the amortized scan). Docstring: the .bed is INDIVIDUAL-LEVEL and stays IN-PERIMETER — never egressed; only the per-region LD .npz crosses (REQ-AOU-LD-EGRESS). Use a hail-optional import so the module still imports on NCSU.

    Tests: create `tests/m3/test_plink_ld_to_npz.py` with the 8 behaviors. Use numpy to fabricate the square `.ld.bin` (raw float32) and a text `.ld.gz` (gzip) + a synthetic `.bim`. For the two aou_ld_panel helpers, test build_plink_ld_command as a pure-string assertion and export_cohort_to_plink with a mock hl (monkeypatch sys.modules['hail']) asserting export_plink called once. pytest.importorskip where a real hail is needed.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_plink_ld_to_npz.py -v --tb=short</automated>
  </verify>
  <acceptance_criteria>
    - `test -f src/python/plink_ld_to_npz.py` exits 0; `wc -l src/python/plink_ld_to_npz.py` returns >= 90.
    - `grep -c "lower_triangular" src/python/plink_ld_to_npz.py` returns >= 2 (the flag is set per mode).
    - `grep -cE "savez_compressed" src/python/plink_ld_to_npz.py` returns >= 1 AND `grep -c "allele_freq" src/python/plink_ld_to_npz.py` returns >= 1 (the .npz contract matches _save_npz).
    - `grep -rn "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/plink_ld_to_npz.py` returns 0 (REQ-PATH-PARAMETERIZATION).
    - `grep -c "keep-allele-order" src/python/aou_ld_panel.py` returns >= 1 (build_plink_ld_command hardcodes it).
    - `grep -c "def build_plink_ld_command\|def export_cohort_to_plink" src/python/aou_ld_panel.py` returns 2.
    - `grep -c "def _write_a3_banded_correlation_bm" src/python/aou_ld_panel.py` returns 1 (the retired m3-02d Hail A.3 write STAYS in the tree — not deleted) AND `grep -nA40 "def export_cohort_to_plink" src/python/aou_ld_panel.py | grep -c "_write_a3_banded_correlation_bm\|row_correlation\|ld_matrix"` returns 0 (the native AFR route never calls the retired Hail A.3 write).
    - `grep -c "in-perimeter\|never egress\|individual-level" src/python/aou_ld_panel.py` returns >= 1 (the .bed egress boundary is documented).
    - `pytest tests/m3/test_plink_ld_to_npz.py -v` reports test_plink_square_bin_to_npz, test_plink_banded_gz_to_npz, test_lower_triangular_flag_correct_per_mode, test_npz_keys_match_save_npz_contract, test_af_sidecar_row_alignment, test_bim_variant_order_preserved, test_canonical_vid_reconstruction_exact, test_build_plink_ld_command_has_keep_allele_order, test_export_cohort_to_plink_invokes_export_plink, test_afr_native_path_does_not_route_through_retired_a3 all PASS (0 failed).
    - `pytest tests/m3 -q` reports 0 failed (no regression; the existing _save_npz / lower_triangular flag-contract tests stay green).
  </acceptance_criteria>
  <done>
    plink_ld_to_npz.py converts native plink1.9 square (`.ld.bin`) OR banded (`.ld.gz`) LD output + `.bim` + AF sidecar into the EXACT egress-clean .npz contract the downstream loader already consumes (ld/variant_ids/rsids/allele_freq/lower_triangular), with the lower_triangular flag CORRECT per mode (square=False, banded=True) so ld_npz_to_rds.R needs no change; aou_ld_panel.py gains export_cohort_to_plink() (one amortized hl.export_plink, .bed stays in-perimeter) + build_plink_ld_command() (--keep-allele-order hardcoded mandatory); all named tests pass; no regression.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2 (m3-02e-T2, autonomous): public EUR LD ($0) — build_public_eur_manifest.py (M2 EUR region -> public UKBB 337k tile mapping + hg19/hg38 adapter; Pan-UKBB 420k documented alternate) + extend download_ukbb_ld_tiles.py for the M3 public source + m3_public_eur_ld.smk rules + tests</name>
  <files>src/python/build_public_eur_manifest.py, src/snakemake/scripts/download_ukbb_ld_tiles.py, src/snakemake/rules/m3_public_eur_ld.smk, Snakefile, tests/m3/test_public_eur_manifest.py</files>
  <read_first>
    - src/snakemake/scripts/download_ukbb_ld_tiles.py (FULL — BUCKET/PREFIX, Tile, list_tiles, load_ld_matrix, load_variant_tsv [cols rsid/chromosome/position/allele1/allele2], safe_region_id, sha256_file, the region->tile overlap + cross-tile concat logic, the main loop over a curated regions CSV)
    - src/snakemake/scripts/ukbb_ld_tile_to_region_rds.py (FULL — the single-tile extractor + .meta.json schema it writes into EUR_ukbb_ld)
    - src/snakemake/rules/ld_reference.smk lines 337-448 (download_ukbb_ld_tiles + build_hgdp_1kg_ld rules — the Snakemake convention + the absolute-path conda-env pattern)
    - config/ld_regions.tsv (the 276 EUR rows: region_id, chr, start/end grch37 AND grch38, region_class)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-effective-rearchitecture.md "Move 1" (Weissbrod 337k vs Pan-UKBB 420k facts: Weissbrod = 2,763 x 3Mb regions, .npz+.gz, s3://broad-alkesgroup-ukbb-ld/, CC-BY, hg19; Pan-UKBB = 420,531, Hail .bm, upper-triangular sparsified, s3://pan-ukb-us-east-1/ld_release/)
    - src/scripts/ld_npz_to_rds.R lines 100-160 (the lower_triangular + liftover handling — the public panel's hg19 tiles feed the SAME .rds contract)
    - data/external/liftover/ (the hg38ToHg19 chain truth; the public panel is hg19 so the adapter maps hg19 public coords <-> the hg38 AFR / hg37 analytic plane)
  </read_first>
  <behavior>
    - test_eur_region_to_tile_mapping: for an M2 EUR region (chr, start, end in the panel's build), build_public_eur_manifest maps it to the overlapping public-panel tile(s); a region within one 3Mb tile maps to one tile; a region spanning two tiles maps to both (cross-tile concat downstream).
    - test_primary_is_weissbrod_337k: the manifest builder's PRIMARY source is the Weissbrod/PolyFun UKBB 337k panel (bucket broad-alkesgroup-ukbb-ld, 3Mb regions, hg19); Pan-UKBB 420k (s3://pan-ukb-us-east-1/ld_release/) is recorded as a DOCUMENTED ALTERNATE (a constant/field, not the default).
    - test_hg19_hg38_coordinate_adapter: the public panel is hg19; the adapter maps a region's coordinates between the panel build (hg19) and the GRCh38-native AFR panel / GRCh37 analytic plane consistently (a known anchor, e.g. an FTO 16q12 coordinate, maps correctly both directions). Assert the adapter does NOT silently treat hg19 panel coords as hg38.
    - test_emitted_extract_jobs_cover_all_eur_regions: every M2 EUR region in config/ld_regions.tsv gets at least one extract job (no EUR region orphaned); the job carries region_id, region_safe, tile key(s), source=EUR_ukbb_pub.
    - test_public_panel_rds_real_round_trip (W-4 — strengthened to an ACTUAL round-trip; the m3-r-ld env is available): build a synthetic public-panel tile slice (hg19), run the m3_public_eur_ld R extract path (ukbb_ld_tile_to_region_rds.py + the liftover) to produce a real EUR_ukbb_pub/{region_safe}.rds, then READ it back (the m3-r-ld env, or pyreadr) and assert: obj$R is a square symmetric matrix, obj$snp_ids/variants present, dimnames present + non-NULL, AND the .meta.json carries the correct build field (hg19 source -> GRCh37 analytic-plane after liftover) + the dimnames count == n_var. If the m3-r-ld R toolchain is unavailable in CI, the test FALLS BACK to asserting the .meta.json build + dimnames-count fields on a fixture .rds (NEVER a pure-doc no-op) and is marked with the m3-r-ld marker so it RUNS (not skips) when the env is present (per the no-skip loader-test discipline).
    - test_snakefile_includes_public_eur_rule: Snakefile includes m3_public_eur_ld.smk.
  </behavior>
  <action>
    Create `src/python/build_public_eur_manifest.py` (NEW, ~90 lines):

    1. Read config/ld_regions.tsv, select the EUR rows. For each, map the region window to the
       overlapping public-panel tile(s). Reuse download_ukbb_ld_tiles.py's Tile/list_tiles overlap
       logic (import it; do NOT re-implement the overlap) — the tiles are 3Mb Weissbrod regions.
    2. Module constants: `EUR_PUBLIC_PRIMARY = {"source": "EUR_ukbb_pub", "panel": "Weissbrod_PolyFun_UKBB_337k", "bucket": "broad-alkesgroup-ukbb-ld", "build": "hg19", "n": 337491, "license": "CC-BY"}` and `EUR_PUBLIC_ALTERNATES = [{"panel": "Pan-UKBB_EUR_420k", "uri": "s3://pan-ukb-us-east-1/ld_release/", "n": 420531, "build": "hg19", "format": "hail_bm_upper_triangular", "note": "documented alternate per D-02e-02; not the default"}]`.
    3. hg19<->hg38 coordinate adapter: a small function (reuse the project's chain/liftover convention — the converter in ld_npz_to_rds.R liftovers GRCh38->GRCh37; the public panel is hg19=GRCh37, so the AFR panel (hg38) and the public EUR panel (hg19) reconcile through the SAME GRCh37 analytic plane per DEC-2026-04-24-01). The adapter maps the M2 region's hg38 window to hg19 for tile selection. Document that rsID-based matching is the robust path where rsIDs exist; coordinate liftover is the fallback.
    4. Emit per-region extract jobs (a TSV/list of dicts) consumed by m3_public_eur_ld.smk; each job: region_id, region_safe, chr, start, end, tile_keys, source.
    5. `argparse` main: --manifest config/ld_regions.tsv --out <jobs.tsv>; REQ-PATH-PARAMETERIZATION (no hardcoded abs paths).

    Extend `src/snakemake/scripts/download_ukbb_ld_tiles.py` (MINIMAL, additive):

    6. Add an EUR_ukbb_pub-aware path constant / output-dir option pointing at
       data/processed/ld_reference/EUR_ukbb_pub (parallel to the existing EUR_ukbb_ld) so the M3
       public-source build does not collide with the legacy curated EUR_ukbb_ld. Do NOT change the
       existing rule's behavior — add the new target dir as a parameter. Keep the build-aware hg19 note.

    Create `src/snakemake/rules/m3_public_eur_ld.smk` (NEW, ~70 lines):

    7. Rule(s) building data/processed/ld_reference/EUR_ukbb_pub/{region_safe}.rds from the public
       panel: download/extract the overlapping tile(s) (reuse download_ukbb_ld_tiles.py /
       ukbb_ld_tile_to_region_rds.py), liftover to the analytic plane, emit the .rds in the loader
       contract. $0 compute (public download only). *** FETCH IS AWS S3, NOT GCS (factual note):
       the Weissbrod panel is fetched via boto3 UNSIGNED (anonymous) from s3://broad-alkesgroup-ukbb-ld/
       — NOT a GCS/AoU path. The download rule therefore needs the S3/boto3 env (envs/ld_build.yml,
       which has boto3 — the SAME env the existing download_ukbb_ld_tiles rule uses), NOT the AoU/GCS
       env. *** Use M3_R_LD_ENV for the R .npz->.rds extract step, and ld_build.yml (boto3 UNSIGNED)
       for the S3 download step. Wire the per-region jobs from build_public_eur_manifest.py.
    8. Add `include: "src/snakemake/rules/m3_public_eur_ld.smk"` to the top-level Snakefile.

    Tests: create `tests/m3/test_public_eur_manifest.py` with the 6 behaviors. Mock the tile listing
    (no S3 hit in CI); use a synthetic EUR-region slice of config/ld_regions.tsv; assert the mapping,
    the primary/alternate constants, the coordinate adapter on a known anchor, full EUR coverage, the
    loader-contract schema, and the Snakefile include (grep).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_public_eur_manifest.py -v --tb=short</automated>
  </verify>
  <acceptance_criteria>
    - `test -f src/python/build_public_eur_manifest.py` exits 0; `wc -l src/python/build_public_eur_manifest.py` returns >= 60.
    - `grep -c "Weissbrod\|337" src/python/build_public_eur_manifest.py` returns >= 1 (PRIMARY) AND `grep -c "Pan-UKBB\|pan-ukb\|420" src/python/build_public_eur_manifest.py` returns >= 1 (documented ALTERNATE).
    - `grep -c "hg19\|hg38\|GRCh37\|GRCh38\|liftover" src/python/build_public_eur_manifest.py` returns >= 2 (the coordinate adapter).
    - `grep -c "EUR_ukbb_pub" src/python/build_public_eur_manifest.py src/snakemake/rules/m3_public_eur_ld.smk` returns >= 2.
    - `grep -rn "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/build_public_eur_manifest.py` returns 0 (REQ-PATH-PARAMETERIZATION).
    - `grep -c "include:.*m3_public_eur_ld.smk" Snakefile` returns 1.
    - `test -f src/snakemake/rules/m3_public_eur_ld.smk` exits 0; `grep -c "EUR_ukbb_pub\|broad-alkesgroup-ukbb-ld" src/snakemake/rules/m3_public_eur_ld.smk` returns >= 1.
    - `grep -c "ld_build.yml\|boto3\|UNSIGNED\|s3" src/snakemake/rules/m3_public_eur_ld.smk` returns >= 1 (the S3/boto3 download env is wired, NOT the GCS/AoU path).
    - `pytest tests/m3/test_public_eur_manifest.py -v` reports the 6 named tests PASS (0 failed).
    - `pytest tests/m3 -q` reports 0 failed.
  </acceptance_criteria>
  <done>
    build_public_eur_manifest.py maps every M2 EUR region to the overlapping public UKBB 337k tile(s) (Weissbrod/PolyFun PRIMARY, Pan-UKBB 420k documented alternate) with an hg19<->hg38 coordinate adapter; download_ukbb_ld_tiles.py is extended (additively) for the EUR_ukbb_pub M3 target; m3_public_eur_ld.smk builds EUR_ukbb_pub/{region_safe}.rds at $0 compute into the loader contract; Snakefile includes it; all named tests pass; no regression.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 3 (m3-02e-T3, autonomous): Move 3 downstream wiring — config/pipeline.yaml EUR chain head = EUR_ukbb_pub (AFR head stays AFR_aou native plink) + the SuSiE-RSS estimate_s z-vs-LD consistency guard on the loaded LD in finemap.smk + resolver/loader tests; record m3-04 as SUPERSEDED-PENDING-REPLAN + state the LD-build boundary EXPLICITLY</name>
  <files>config/pipeline.yaml, src/snakemake/rules/finemap.smk, tests/m3/test_ld_panel_resolver.py, tests/m3/test_finemap_loader_contract.py</files>
  <read_first>
    - config/pipeline.yaml lines 200-228 (the ld_panel: block — EUR/AFR/TRANS chains, strict_aou_only, pin)
    - src/python/ld_panel.py (FULL — resolve_ld_path: chain walk, pin, strict_aou_only, region_id/region_safe substitution)
    - src/snakemake/rules/finemap.smk (FULL — run_finemap rule; the ld_matrix input wired via resolve_ld_path in m3-03; where the estimate_s guard hooks on the loaded LD)
    - src/legacy/region_analysis/scripts/run_susie_rss.R (the existing susie_rss call convention — does it already call estimate_s/kriging_rss? wire the guard consistently)
    - tests/m3/test_ld_panel_resolver.py (FULL — existing chain-resolution tests + fixtures) + tests/m3/test_finemap_loader_contract.py (FULL — the resolve_ld_path -> load_ld_matrix -> susie_rss contract)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-effective-rearchitecture.md "Move 3" (estimate_s/kriging_rss z-vs-LD diagnostic, Zou 2022)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md "Phase Boundary" + D-M3-02/03 (322 = pre-m3-02d 161 union x 2 ancestries; 276 = post-m3-02d per-ancestry AFR window count)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-04-W4-production-and-egress-PLAN.md (FULL — the STALE 322-cell HAIL LD production fire being SUPERSEDED: truth line ~24, objective ~63, Task 2 line ~269 routes ~92 regions through the retired A.3 BlockMatrix path for BOTH AFR_aou + EUR_aou)
  </read_first>
  <behavior>
    - test_eur_chain_head_is_public: resolve_ld_path for a representative EUR region resolves to the EUR_ukbb_pub source (chain head) when its .rds exists; the legacy EUR_aou/EUR_ukbb/EUR_1kg remain in the chain as fallbacks BEHIND it.
    - test_afr_chain_head_unchanged: the AFR chain head stays AFR_aou (the native-plink .npz->.rds path is unchanged); the AFR fallback tail (AFR_hgdp, AFR_1kg) is unchanged.
    - test_eur_pin_to_public_works: pinning EUR to EUR_ukbb_pub resolves only the public panel; pinning to a source not in the chain still raises ValueError (back-compat).
    - test_estimate_s_guard_surfaced_as_new_per_region_capture (W-2 — must prove NEW work; the pre-existing kriging_rss at run_susie_rss.R:611 is NOT sufficient): assert finemap.smk gained a NEW per-region s-diagnostic CAPTURE/LOG (a log: directive or a captured-output artifact path for the estimate_s/kriging_rss s-estimate) AND a NEW m3-02e comment block tying the guard to the two new LD sources (--keep-allele-order native AFR + public-EUR liftover). The test FAILS if the only match is the pre-existing run_susie_rss.R:611 kriging_rss line (i.e. it must find a NEW finemap.smk capture line + a NEW comment, not just grep kriging_rss>=1). If the s-estimate is surfaced by wiring run_susie_rss.R to RETURN/serialize a per-region s scalar (new code), assert that new return/serialization line too.
    - test_loader_contract_unchanged_for_both_sources: the existing resolve_ld_path -> load_ld_matrix contract test stays GREEN for BOTH the AFR native .npz->.rds and the public EUR .rds (one loader contract, two sources).
    - test_m3_04_recorded_superseded: a documented assertion (a comment/marker in finemap.smk AND a note in the SUMMARY/frontmatter) that (a) the M3 LD-build (AFR native-plink ~276 windows + public EUR) is COMPLETE within m3-02e, and (b) m3-04-W4-production-and-egress-PLAN.md (the stale 322-cell HAIL LD fire) is SUPERSEDED-PENDING-REPLAN — it must CONSUME m3-02e's .npz/.rds, not rebuild LD via Hail. The comment states the correct division (322 = pre-m3-02d 161x2 basis; 276 = post-m3-02d per-ancestry AFR count; coloc/SuSiE fine-mapping is M4). The boundary is explicit, not implicit.
  </behavior>
  <action>
    In `config/pipeline.yaml`:

    1. Add `EUR_ukbb_pub` as the EUR chain HEAD, ahead of the existing EUR_aou/EUR_ukbb/EUR_1kg:
       `- {source: "EUR_ukbb_pub", path: "data/processed/ld_reference/EUR_ukbb_pub/{region_safe}.rds"}`.
       Keep the legacy entries as fallbacks. AFR chain head stays AFR_aou (unchanged). Update the
       pin block comment to note EUR_ukbb_pub is pinnable. Document inline that for M3 the EUR LD is
       the public UKBB 337k reference (D-02e-02) and the AFR LD is the native-plink AoU panel.

    In `src/snakemake/rules/finemap.smk`:

    2. Wire the SuSiE-RSS `estimate_s` (z-vs-LD consistency) diagnostic as a per-region guard on the
       loaded LD (Zou 2022). If run_susie_rss.R already exposes estimate_s/kriging_rss, route the
       finemap rule to capture/log the s-estimate per region and FLAG regions where s indicates a
       z-vs-LD mismatch (the allele-flip/encoding failure --keep-allele-order + public-EUR liftover
       are most exposed to). Add a top-of-rule comment block: "m3-02e Move 3: estimate_s z-vs-LD
       consistency guard (Zou 2022) — the native-plink AFR LD (--keep-allele-order) and the public
       EUR liftover are the two new sources; estimate_s catches allele-flip/encoding mismatch per
       region." If the susie invocation lives only in the R script, wire the guard there and have the
       smk rule surface the diagnostic output as a logged artifact.
    3. Add the explicit supersede + boundary comment block to finemap.smk: "m3-02e (B-1): the M3
       LD-BUILD is COMPLETE within m3-02e — AFR LD = the ~276 native-plink per-ancestry windows
       (Task 4 in-perimeter fire) + EUR LD = the public UKBB 337k panel (Task 2, $0). The Hail
       BlockMatrix LD path is RETIRED. m3-04-W4-production-and-egress-PLAN.md is the STALE 322-cell
       HAIL LD production fire (322 = pre-m3-02d 161 union regions x 2 ancestries; 276 = the
       post-m3-02d per-ancestry AFR window count) and is SUPERSEDED-PENDING-REPLAN: it must be
       re-planned to CONSUME m3-02e's AFR-native .npz + public EUR .rds, NOT to rebuild LD via Hail
       (which would spend the 160-260 cluster-h the cost re-architecture exists to avoid). The
       downstream coloc/SuSiE fine-mapping fire is a separate M4 concern, unaffected." Also surface
       this in the SUMMARY. (This is the lower-risk B-1 option: it does NOT rewrite m3-04 inside this
       wave — it records m3-04 as superseded so no one fires the stale Hail plan after m3-02e lands.)

    Tests: extend `tests/m3/test_ld_panel_resolver.py` with test_eur_chain_head_is_public,
    test_afr_chain_head_unchanged, test_eur_pin_to_public_works (build a tmp ld_panel config + tmp
    .rds files; assert resolution). Extend `tests/m3/test_finemap_loader_contract.py` with
    test_estimate_s_guard_present (grep/contract on finemap.smk + run_susie_rss.R for the estimate_s
    wiring), test_loader_contract_unchanged_for_both_sources, test_production_boundary_documented.
    Keep the existing no-skip loader test green.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_ld_panel_resolver.py tests/m3/test_finemap_loader_contract.py -v --tb=short</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "EUR_ukbb_pub" config/pipeline.yaml` returns >= 1 AND the EUR_ukbb_pub line appears BEFORE the EUR_aou line within the EUR chain (header-ordered check: `awk '/^  EUR:/{f=1} f&&/EUR_ukbb_pub/{print NR; exit}' config/pipeline.yaml` < the EUR_aou line number).
    - `grep -c "AFR_aou" config/pipeline.yaml` returns >= 1 (AFR head unchanged).
    - W-2 (prove NEW work, not the pre-existing run_susie_rss.R:611 kriging_rss): `grep -c "estimate_s\|kriging_rss\|s_diagnostic\|ld_z_consistency" src/snakemake/rules/finemap.smk` returns >= 1 (a NEW capture/log line ADDED to finemap.smk — it had ZERO before) AND `grep -c "m3-02e\|--keep-allele-order\|public-EUR liftover" src/snakemake/rules/finemap.smk` returns >= 1 (the NEW comment block). If the s-estimate is surfaced by new code in run_susie_rss.R, `git diff --stat src/legacy/region_analysis/scripts/run_susie_rss.R` shows the file changed. The pre-existing kriging_rss at run_susie_rss.R:611 alone does NOT satisfy this criterion.
    - `grep -c "SUPERSEDED-PENDING-REPLAN\|m3-04" src/snakemake/rules/finemap.smk` returns >= 1 AND the comment block states BOTH that the M3 LD-build is complete within m3-02e AND that m3-04 (the stale 322-cell Hail LD fire) must be re-planned to consume m3-02e outputs (grep for "consume" + "Hail" + "276"/"322" in the same comment block).
    - `pytest tests/m3/test_ld_panel_resolver.py -v` reports test_eur_chain_head_is_public, test_afr_chain_head_unchanged, test_eur_pin_to_public_works PASS.
    - `pytest tests/m3/test_finemap_loader_contract.py -v` reports test_estimate_s_guard_present, test_loader_contract_unchanged_for_both_sources, test_production_boundary_documented PASS AND the existing no-skip loader contract test stays green.
    - `python -c "from src.python.ld_panel import resolve_ld_path; print('OK')"` exits 0 (resolver still importable).
    - `pytest tests/m3 -q` reports 0 failed.
  </acceptance_criteria>
  <done>
    config/pipeline.yaml EUR chain head is the public UKBB 337k panel (EUR_ukbb_pub) ahead of the legacy entries with the AFR head unchanged (AFR_aou native plink); the SuSiE-RSS estimate_s z-vs-LD consistency guard is wired on the loaded LD in the finemap path (Zou 2022, guarding the allele-flip/encoding mismatch the two new sources are exposed to); the M3 LD-build is recorded COMPLETE within m3-02e (AFR native-plink ~276 windows + public EUR) and m3-04 (the stale 322-cell HAIL LD production fire) is recorded SUPERSEDED-PENDING-REPLAN — must consume m3-02e outputs, not rebuild LD via Hail (322 = pre-m3-02d 161x2; 276 = post-m3-02d per-ancestry AFR count; coloc/SuSiE fine-mapping = M4); all named + existing loader/resolver tests pass.
  </done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 4 (m3-02e-T4, autonomous:false — Carter fires; the ONLY billable task): in-perimeter export-once + native plink LD loop over 276 AFR regions on a single Spot VM -> egress-clean .npz panel + real-cost panel TSV + verified shutdown (token-free handback)</name>
  <what-built>
    Tasks 1-3 deliver the autonomous NCSU code+tests: plink_ld_to_npz.py (the native-plink LD reader),
    export_cohort_to_plink() + build_plink_ld_command() (--keep-allele-order mandatory) in
    aou_ld_panel.py, build_public_eur_manifest.py + m3_public_eur_ld.smk (public EUR LD, $0), and the
    resolver + estimate_s wiring (Move 3). The turnkey runbook for THIS in-perimeter fire is the
    deliverable of Tasks 1-3:
    `.planning/phases/m3-aou-afr-ld-panel-build/m3-02e-AFR-NATIVE-FIRE-BRIEF.md`
    (authored as part of this plan's autonomous work — see <action> below). It is self-contained and
    token-free (AoU cat's the artifacts back; NCSU reconstructs + pushes — NO Workbench push token,
    per feedback_push_ncsu_before_aou_clone_fire).
  </what-built>
  <action>
    AUTONOMOUS (done by the executor as part of Tasks 1-3, NOT at the gate): author
    `.planning/phases/m3-aou-afr-ld-panel-build/m3-02e-AFR-NATIVE-FIRE-BRIEF.md` as the turnkey runbook
    for Carter to fire. The brief MUST contain, in order:

    1. PREFLIGHT (free): git pull + checkout -f on the cluster home; confirm origin tip == local HEAD
       (push NCSU first per feedback_push_ncsu_before_aou_clone_fire); confirm the AFR cohort MT at
       gs://rw-migration-aou-rw-476cdac2/ld/mt_afr_qc.mt (count_cols == 73,122; the /ld/ path NOT
       /ld/mt/ — readers read URIs literally); confirm the 276 AFR compute windows in
       config/ld_regions.tsv.
    2. EXPORT-ONCE: run export_cohort_to_plink(mt_afr_qc, <bfile_prefix>) — one hl.export_plink, the
       count_cols scan paid ONCE (~20 min per the pilot). The .bed/.bim/.fam is INDIVIDUAL-LEVEL and
       STAYS IN-PERIMETER — never egress it.
    3. PRODUCTION-VM RE-MEASURE GATE (the pilot caveat): before committing the full 276-region budget,
       run plink_ld_to_npz's plink command (build_plink_ld_command, square bin4, --keep-allele-order)
       on ONE representative region on the ACTUAL production VM type and re-measure wall/RAM (the
       pilot's $4.19/$1.49 rates are labelled n2-highmem-64 but the pilot ran on n2-standard-16). If
       the re-measured x276 projection blows the budget, STOP and re-cost before the loop.
    4. THE LOOP: loop the 276 AFR windows on a single Spot VM running
       `plink1.9 --bfile <cohort> --keep-allele-order --chr {chr} --from-bp {window_start} --to-bp
       {window_end} --r square bin4 --out {region}` (banded `--r gz` + r2 floor is the disk-tight
       alternate). For each region, run plink_ld_to_npz.py (square mode) -> the egress-clean .npz
       (ld/variant_ids/rsids/allele_freq/lower_triangular=False). Record per-region
       wall_min/peak_ram_gib/output_gib/n_var into m3-W2-native-plink-panel.tsv (the REAL
       production-cost measurement; this REPLACES the one-cell pilot TSV as the cost basis).
    5. VERIFY (D-M3-10): per region, gsutil du + a numpy read-back (shape (n_var,n_var), diag==1.0,
       symmetric, dtype float32) — file existence / a _SUCCESS-style marker is NOT evidence.
    6. EGRESS: bundle per-chromosome via ld_egress_bundle.plan_egress_bundles (reuse m3-02d), split
       any chrom bundle > the 50 GB working ceiling into chrN_a/chrN_b, egress ONLY the aggregate LD
       .npz + AF (never the .bed). Append the per-chromosome egress entries to aou-egress-audit-log.md.
    7. SHUTDOWN: STOP the VM/cluster; write m3-02e-cluster-shutdown.md with the verified Stopped
       badge + $-spent; token-free handback (cat the panel TSV + shutdown record); ping NCSU
       "native-panel-recorded" -> NCSU reconstructs + pushes.

    Include the PILOT GOING-IN NUMBERS (square 56.224 min/region -> 258.6 VM-h -> $385 Spot /
    $1,084 on-demand x276; banded 25.446 min -> 117.05 VM-h -> $174/$490) and the three pilot
    caveats (production-VM re-measure; banded ~400M-pair estimate; export ~33s/region + one-time
    count_cols ~20min) as explicit GATE conditions, not footnotes.
  </action>
  <how-to-verify>
    Carter fires the brief in the AoU perimeter (this is the ONLY billable step in m3-02e; the gate
    `--auto` cannot cross it). Verification at the gate, in order:
    1. The AFR cohort exported ONCE to plink .bed/.bim/.fam in-perimeter (count_cols == 73,122 logged
       once; the .bed never leaves the perimeter).
    2. The production-VM re-measure ran on one region and the x276 projection is within budget BEFORE
       the full loop (the pilot-caveat gate).
    3. The 276-region plink loop completed with --keep-allele-order on every call; each region landed
       a square float32 .npz (diag==1.0, symmetric) data-layer-verified (gsutil du + numpy read-back,
       NOT a marker) per D-M3-10.
    4. m3-W2-native-plink-panel.tsv carries the REAL per-region walls/RAM/output/n_var (the real
       production cost, not extrapolated from one pilot cell).
    5. Per-chromosome egress bundles filed under the 50 GB working ceiling; ONLY aggregate LD+AF
       egressed; aou-egress-audit-log.md updated.
    6. The VM/cluster is verified STOPPED ($0 idle) with m3-02e-cluster-shutdown.md.
    7. Token-free handback completed; NCSU reconstructed + pushed the panel TSV + shutdown record;
       origin tip == local HEAD.
  </how-to-verify>
  <resume-signal>Type "native-panel-recorded" (then NCSU reconstructs + pushes), or describe issues / a re-measure budget overrun / a verification failure.</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| AoU perimeter (individual-level WGS / plink .bed) ↔ NCSU GPFS (aggregate LD .npz) | The plink cohort .bed/.bim/.fam is individual-level and computed IN-PERIMETER; ONLY the per-region aggregate LD matrix (variant×variant r) + AF crosses egress. The .bed never leaves. |
| Public UKBB 337k panel (hg19, external) ↔ M3 analytic plane (hg38 AFR / hg37 canonical) | The public EUR reference is a different build; the hg19↔hg38 adapter + rsID matching reconcile it. A silent build mismatch would misalign LD with GWAS z. |
| Native-plink LD (--keep-allele-order) ↔ GWAS z-scores (susieR) | LD allele order must match the GWAS z allele order or signs flip → susieR failure. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M3-02e-EGR | Information disclosure | export_cohort_to_plink .bed | mitigate | The .bed/.bim/.fam is individual-level and stays in-perimeter (code comment + fire brief boundary); only the aggregate LD .npz + AF is egressed; egress goes through ld_egress_bundle per-chromosome under the 50 GB working ceiling; per-chrom entries logged to aou-egress-audit-log.md. AFR LD .npz is egress-clean per the prior G0 ruling. |
| T-M3-02e-SIGN | Tampering / correctness | build_plink_ld_command --keep-allele-order | mitigate | --keep-allele-order is hardcoded into build_plink_ld_command (not optional); a test asserts it is always present. The estimate_s z-vs-LD guard (Move 3) catches any residual allele-flip/encoding mismatch per region. |
| T-M3-02e-TRI | Tampering / correctness | plink_ld_to_npz lower_triangular flag | mitigate | square→lower_triangular=False, banded→lower_triangular=True; a test asserts the flag per mode (the project's twice-bitten halving/doubling failure: CR-01 + BR-01). ld_npz_to_rds.R honors the flag authoritatively. |
| T-M3-02e-BUILD | Tampering / provenance | public EUR hg19↔hg38 adapter | mitigate | The adapter never treats hg19 panel coords as hg38 (a test asserts a known anchor maps both directions); rsID matching is the robust path; ld_npz_to_rds.R records the chain SHA-256 in provenance. |
| T-M3-02e-COST | Availability / budget | the in-perimeter fire | mitigate | The fire brief re-measures the production-VM wall on ONE region before committing the 276-region budget (the pilot ran n2-standard-16 but the $-rates are labelled n2-highmem-64); a budget-overrun at the re-measure gate STOPS the loop. Spot VM at ~$1.49/hr; verified shutdown artifact. |
| T-M3-02e-VERIFY | Repudiation / data integrity | per-region .npz verification | mitigate | D-M3-10: each .npz is contents-validated (gsutil du + numpy shape/diag/symmetry read-back); file existence / markers are NEVER sufficient evidence. |
</threat_model>

<verification>
**m3-02e phase-level checks:**

1. `pytest tests/m3 -q` reports 0 failed (Tasks 1-3 add the plink->npz, public-EUR, resolver/estimate_s tests; all existing m3 tests stay green).
2. `test -f src/python/plink_ld_to_npz.py && test -f src/python/build_public_eur_manifest.py` exits 0.
3. `grep -c "keep-allele-order" src/python/aou_ld_panel.py` returns >= 1 (mandatory plink flag).
4. `grep -c "lower_triangular" src/python/plink_ld_to_npz.py` returns >= 2 (correct flag per mode).
5. `grep -c "EUR_ukbb_pub" config/pipeline.yaml` returns >= 1 (public EUR chain head).
6. W-2: `grep -c "estimate_s\|kriging_rss\|s_diagnostic" src/snakemake/rules/finemap.smk` returns >= 1 (a NEW per-region s-diagnostic capture line ADDED to finemap.smk — it had none before; the pre-existing run_susie_rss.R:611 kriging_rss does NOT count).
7. `grep -c "include:.*m3_public_eur_ld.smk" Snakefile` returns 1.
8. `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-02e-AFR-NATIVE-FIRE-BRIEF.md` exits 0 (the turnkey fire brief is the autonomous deliverable that the Task 4 gate consumes).
9. (Gated, post-fire) m3-W2-native-plink-panel.tsv carries real per-region walls; m3-02e-cluster-shutdown.md confirms $0 idle.
</verification>

<success_criteria>
- plink_ld_to_npz.py converts native plink square/banded LD into the egress-clean .npz contract with the correct lower_triangular flag per mode (square=False, banded=True); ld_npz_to_rds.R needs no change.
- aou_ld_panel.py has export_cohort_to_plink() (one amortized hl.export_plink; .bed stays in-perimeter) + build_plink_ld_command() (--keep-allele-order hardcoded mandatory).
- build_public_eur_manifest.py + m3_public_eur_ld.smk build the public UKBB 337k EUR panel ($0 compute) into the loader contract; Pan-UKBB 420k documented alternate; hg19↔hg38 adapter present.
- config/pipeline.yaml EUR chain head = EUR_ukbb_pub (public 337k) ahead of legacy; AFR head = AFR_aou (native plink) unchanged.
- The SuSiE-RSS estimate_s z-vs-LD guard is wired on the loaded LD (Zou 2022) for the two new sources.
- The M3 LD-build is recorded COMPLETE within m3-02e (AFR native-plink ~276 windows + public EUR); m3-04 (the stale 322-cell HAIL LD production fire) is recorded SUPERSEDED-PENDING-REPLAN (must consume m3-02e .npz/.rds, not rebuild LD via Hail). 322 = pre-m3-02d 161x2; 276 = post-m3-02d per-ancestry AFR count; coloc/SuSiE fine-mapping is a separate M4 concern.
- The turnkey AFR-native fire brief is authored (export-once → plink loop → .npz → verify → egress → shutdown → token-free handback; production-VM re-measure gate; PILOT going-in numbers).
- (Gated) the fire produces the real-cost native-plink panel TSV + the verified shutdown artifact.
- All NON-fire tasks are autonomous; the in-perimeter fire is the only autonomous:false task.
- The Hail BlockMatrix ~34k-cluster-h path is NOT taken; the m3-02d ordering-B A.3 write stays in the tree as the retired Hail path (not deleted, not the AFR route).
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-02e-W2-native-ld-export-and-public-eur-SUMMARY.md` recording:
- Files created/modified + lines added (plink_ld_to_npz.py, the two aou_ld_panel helpers, build_public_eur_manifest.py, m3_public_eur_ld.smk, the resolver/estimate_s wiring, the fire brief).
- Pytest pass count (tests/m3) + the new test names.
- The EXPLICIT supersede record: M3 LD-build COMPLETE within m3-02e (AFR native-plink ~276 windows + public EUR); m3-04 (stale 322-cell HAIL LD fire) = SUPERSEDED-PENDING-REPLAN, must consume m3-02e outputs not rebuild LD via Hail (322 = pre-m3-02d 161x2; 276 = post-m3-02d per-ancestry AFR count; coloc/SuSiE fine-mapping = M4).
- The D-02e-01/02/03 auto-selected decisions + any Carter override.
- (Post-fire, after the handback) the real per-region production-VM walls from m3-W2-native-plink-panel.tsv vs the pilot going-in numbers, and the final AFR-panel cost vs the $3-4k budget.
- Any open risks (production-VM re-measure outcome; banded vs square disk footprint; public-EUR liftover anchor verification).
</output>
</content>
</invoke>
