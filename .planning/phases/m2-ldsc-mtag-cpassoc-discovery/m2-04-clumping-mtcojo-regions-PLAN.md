---
phase: m2-ldsc-mtag-cpassoc-discovery
plan: 04
type: execute
wave: 4
depends_on: [m2-00-preflight-and-environment, m2-01-ldsc-matrix-refire, m2-02-mtag-3-strata, m2-03-cpassoc-3-strata]
autonomous: true
requirements: [REQ-MTAG-OVERLAP, REQ-CPASSOC-ORTHOGONAL]
task_count: 3
files_modified:
  - src/snakemake/rules/m2_clumping.smk
  - src/snakemake/rules/m2_mtcojo.smk
  - src/snakemake/rules/m2_regions.smk
  - src/python/build_region_union.py
  - src/python/select_mtcojo_eligible_targets.py
  - data/processed/clumping/{ancestry}/
  - data/processed/clumping/{ancestry}/{trait}.{ancestry}.{consortium}.{year}.LD-1000G-{ldpop}.clumped.bed
  - data/processed/mtcojo/{stratum}/mtcojo_eligible_targets.tsv
  - data/processed/mtcojo/{stratum}/{trait}.mtcojo.cojo
  - data/processed/mtcojo/{stratum}/mtcojo_sensitivity.tsv
  - results/regions/union_region_list.bed
must_haves:
  truths:
    - "src/snakemake/rules/m2_clumping.smk fires plink=1.9 --clump per (trait × ancestry × chr) producing data/processed/clumping/{ancestry}/{trait}.*.LD-1000G-{ldpop}.chr{N}.clumped — one BED per cell"
    - "PLINK invocation includes literal flags: --clump --clump-p1 5e-8 --clump-p2 1 --clump-r2 0.01 --clump-kb 1000 (D-M2-09)"
    - "EUR-stratum cells consume LD reference data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC.{chr} (existing); AFR-stratum cells consume data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{chr} (Wave 0 Task 4 build); TRANS-stratum cells use 1000G EUR per D-M2-Q3 + RESEARCH Q4"
    - "src/python/select_mtcojo_eligible_targets.py emits data/processed/mtcojo/{stratum}/mtcojo_eligible_targets.tsv listing (target_trait) tuples where MTAG produced a novel locus AND any contributing-trait gcov_int > 0.1 in the LDSC matrix (D-M2-08 + D-M2-Q5)"
    - "src/snakemake/rules/m2_mtcojo.smk runs gcta --mtcojo-file per eligible (stratum, target_trait) producing data/processed/mtcojo/{stratum}/{trait}.mtcojo.cojo + sensitivity table mtcojo_sensitivity.tsv"
    - "TRANS mtCOJO runs with 1000G EUR primary LD reference + 1000G AFR sensitivity check column (D-M2-Q3 + Q4) — concordance reported in mtcojo_sensitivity.tsv as trans_ld_panel_concordance"
    - "src/python/build_region_union.py emits results/regions/union_region_list.bed with strict bedtools default merge (no -d, no -s flags per Q6 + Pitfall 9) over ±1 Mb windows around clumped + MTAG-novel + CPASSOC-novel leads, with provenance JSON column listing {clump, mtag, cpassoc} contributors per region (D-M2-09)"
  artifacts:
    - path: "src/snakemake/rules/m2_clumping.smk"
      provides: "Per-(trait × ancestry × chr) PLINK 1.9 clumping rule + per-(trait × ancestry) aggregator BED"
      min_lines: 80
    - path: "src/snakemake/rules/m2_mtcojo.smk"
      provides: "Per-(stratum, target_trait) mtCOJO sensitivity rule + sensitivity table aggregator (D-M2-08, D-M2-Q3, D-M2-Q5)"
      min_lines: 80
    - path: "src/snakemake/rules/m2_regions.smk"
      provides: "Region union builder rule consuming clumped + MTAG-novel + CPASSOC-novel leads"
      min_lines: 40
    - path: "src/python/build_region_union.py"
      provides: "Strict bedtools-default merge + provenance JSON column emitter (D-M2-09 + Q6 + Pitfall 9)"
      min_lines: 100
    - path: "src/python/select_mtcojo_eligible_targets.py"
      provides: "D-M2-Q5 eligible-target selector — joins MTAG-novel hit lists with LDSC bivariate-intercept matrix at gcov_int > 0.1 threshold"
      min_lines: 60
    - path: "results/regions/union_region_list.bed"
      provides: "ROADMAP M2 success criterion 4 — genome-wide union region BED (~1500-3000 regions expected per amendment)"
  key_links:
    - from: "data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt + data/processed/cpassoc/{stratum}/cpassoc_results.tsv + data/processed/clumping/{ancestry}/*.clumped"
      to: "results/regions/union_region_list.bed"
      via: "build_region_union.py — bedtools default merge over ±1 Mb windows + provenance JSON"
      pattern: "build_region_union|union_region_list"
    - from: "data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt + bivariate_intercept_matrix_2026-04-M2.tsv"
      to: "data/processed/mtcojo/{stratum}/mtcojo_eligible_targets.tsv"
      via: "select_mtcojo_eligible_targets.py — gcov_int > 0.1 filter (D-M2-08 + D-M2-Q5)"
      pattern: "gcov_int.*0.1"
---

<objective>
Wave 4 closes the discovery phase by producing the region-list deliverable (ROADMAP M2 success criterion 4) and the mtCOJO sensitivity table (success criterion 6). Three orthogonal pieces:

1. **PLINK clumping** (`m2_clumping.smk`) — per (trait × ancestry × chr) `plink=1.9 --clump` invocations using the canonical D-M2-09 thresholds (p1=5e-8, p2=1, r²<0.01, kb=1000). Pitfall 5 enforced: PLINK 2.0 has no --clump; we use PLINK 1.9 from envs/m2-clumping.yml. EUR uses the existing 1000G_EUR_Phase3_plink panel; AFR uses the Wave 0 Task 4-built 1000G_AFR_Phase3_plink; TRANS uses 1000G EUR (D-M2-Q3 + RESEARCH Q4 default; AFR sensitivity is a Wave 4 robustness add).

2. **mtCOJO sensitivity** (`m2_mtcojo.smk` + `select_mtcojo_eligible_targets.py`) — D-M2-08 + D-M2-Q5 require running mtCOJO ONLY for (stratum, target_trait) tuples where MTAG produced a novel locus AND any contributing-trait gcov_int > 0.1. The eligible-targets selector joins MTAG-novel hit lists from Wave 2 with the LDSC bivariate-intercept matrix from Wave 1 to compute the eligibility list. mtCOJO is then fired per-target via gcta=1.94 (envs/m2-mtcojo.yml). TRANS mtCOJO uses 1000G EUR LD primary; 1000G AFR LD sensitivity check is added as an optional re-run column per D-M2-Q3.

3. **Region union BED** (`m2_regions.smk` + `build_region_union.py`) — D-M2-09 + Q6 + Pitfall 9: strict bedtools default merge (no -d, no -s) over ±1 Mb windows around (clumped leads ∪ MTAG-novel leads ∪ CPASSOC-novel leads). Output at `results/regions/union_region_list.bed` with chr, start, end, region_id, score=., strand=., provenance_json columns. Provenance JSON encodes which methods + strata contributed to each merged region so downstream M4 can prioritize Tier 1 = MTAG ∩ CPASSOC regions. Expected count ~1,500-3,000 per amendment text (assumption A — actual count drives M3+M4 budget).

This is the largest production fire of M2 by compute (~3 hr clumping + ~30 min mtCOJO + ~5 min region union). Output: ROADMAP success criteria 4 + 6 satisfied; M3 hand-off region list frozen.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-00-preflight-and-environment-PLAN.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-01-ldsc-matrix-refire-PLAN.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-02-mtag-3-strata-PLAN.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-03-cpassoc-3-strata-PLAN.md
@CLAUDE.md
@src/snakemake/rules/m2_reference.smk
@src/python/m2_stratum_keys.py
@envs/m2-clumping.yml
@envs/m2-mtcojo.yml
@envs/m2-regions.yml
@config/trait_inventory.yaml
@data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv
@data/processed/ldsc_overlap/rg_matrix_long_M2.tsv

<interfaces>
**PLINK 1.9 --clump CLI (Pitfall 5 — only PLINK 1.9 has --clump):**
```bash
plink \
    --bfile data/reference/ldsc/1000G_{ldpop}_Phase3_plink/1000G.{ldpop}.QC.{chr} \
    --clump <sumstats path with SNP+P columns> \
    --clump-snp-field SNP \
    --clump-field P \
    --clump-p1 5e-8 \
    --clump-p2 1 \
    --clump-r2 0.01 \
    --clump-kb 1000 \
    --memory 3500 \
    --out <out_prefix>
```
Output: {out_prefix}.clumped (text format, columns CHR F SNP BP P TOTAL NSIG S05 S01 S001 S0001 SP2). Convert to BED: chr, start=BP-1, end=BP, name=SNP, score=., strand=. (lead SNPs become 1bp BED entries; ±1 Mb windows applied at union step).

**Trait-ancestry harmonized sumstats (per M1 D-16 naming, GZIP-bgzip):**
- data/processed/sumstats_harmonized/{trait}.{ancestry}.{consortium}.{year}.GRCh37.tsv.bgz (or `.parquet`)
- For PLINK clump: needs columns SNP + P; the M1 munged HM3 .sumstats.gz at data/processed/ldsc_overlap/munged/ has SNP + Z + N (not P); compute P = `2 * scipy.stats.norm.sf(abs(Z))` OR use the harmonized .tsv.bgz which has the original P column.

**Decision: clump from harmonized sumstats (NOT munged HM3) — has the original P column at full SNP density (~10M not 1M).**

**mtCOJO CLI (GCTA 1.94 bundled):**
```bash
gcta \
    --bfile <ld reference bfile prefix> \
    --mtcojo-file <mtcojo input list path> \
    --w-ld-chr <ld score directory> \
    --ref-ld-chr <ld score directory> \
    --out <out_prefix>
```
The `--mtcojo-file` is a 2-column TSV listing (trait_label, harmonized_sumstats_path) for the target trait first then the covariate traits. For each (stratum, target_trait) tuple that the eligible-targets selector emits, this rule fires once with target_trait first.

**Output columns of {trait}.mtcojo.cojo:**
SNP, A1, A2, freq, b, se, p, N, b_cojo, se_cojo, p_cojo  — joined with MTAG-novel hit list to produce mtcojo_sensitivity.tsv.

**MTAG-novel lead extraction:** read data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt; filter to rows with mtag_pval < 5e-8 AND max_FDR < 0.05; the lead SNPs per ±1 Mb LD-block (within-stratum; can be derived from clumping the MTAG output OR by simple p-value sort + ±1 Mb pruning).

**CPASSOC-novel lead extraction:** read data/processed/cpassoc/{stratum}/cpassoc_results.tsv; filter to rows with SHom_p < 5e-8 OR SHet_p < 5e-8; extract lead per ±1 Mb LD-block.

**bedtools merge for union (Q6 + Pitfall 9):**
```bash
bedtools merge -i <sorted input.bed> > <merged.bed>
# NO -d flag (default 0 — strict overlap)
# NO -s flag (Pitfall 9 — strands meaningless for genomic regions)
```

**LD score directories for mtCOJO:**
- EUR: data/external/ldscore/eur_w_ld_chr/ (existing)
- AFR: same EUR scores per D-M2-Q2 cross-ancestry approximation; M3-supersede when AoU AFR LD lands
- TRANS: 1000G EUR primary (D-M2-Q3) + 1000G AFR sensitivity (re-run with `--ref-ld-chr` flipped; report concordance column)
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: src/snakemake/rules/m2_clumping.smk + production fire — per (trait × ancestry × chr) PLINK 1.9 clump (D-M2-09, Pitfall 5)</name>
  <files>src/snakemake/rules/m2_clumping.smk, data/processed/clumping/{ancestry}/</files>
  <read_first>
    - src/snakemake/rules/m2_reference.smk (Wave 0 Task 4 — provides 1000G AFR PLINK bfile dependency)
    - envs/m2-clumping.yml (Wave 0 Task 2 — provides plink=1.9 per Pitfall 5)
    - config/trait_inventory.yaml (47 cells; the active set with sha256_harmonized + qc_status != MISSING is the input universe)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Q3" lines 184-235 (full PLINK rule shape with memory budget)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §D-M2-09 lines 114-125
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §D-M2-Q3 lines 254-258
    - tests/m2/test_plink_clump_invocation.py (the RED test from Wave 0 — assert flag list)
  </read_first>
  <action>
    Author `src/snakemake/rules/m2_clumping.smk` per RESEARCH Q3 rule shape:

    ```python
    """M2 Wave 4 — Per-(trait × ancestry × chr) PLINK 1.9 clumping.

    Plan: m2-04-clumping-mtcojo-regions-PLAN.md.
    Decisions: D-M2-09 (clump thresholds: p1=5e-8, p2=1, r²<0.01, kb=1000),
               D-M2-02 (provisional 1000G AFR LD; M3-supersede commitment),
               D-M2-Q3 (TRANS uses 1000G EUR primary + AFR sensitivity).
    Pitfall 5: PLINK 2.0 does NOT have --clump; envs/m2-clumping.yml pins plink=1.9.
    """
    from pathlib import Path
    import os, sys, yaml

    try:
        _BASE = Path(workflow.basedir)  # type: ignore[name-defined]
    except NameError:
        _BASE = Path(os.getcwd())

    def _find_project_root(start: Path) -> Path:
        cur = start.resolve()
        for _ in range(6):
            if (cur / "config" / "pipeline.yaml").is_file():
                return cur
            if cur.parent == cur:
                break
            cur = cur.parent
        return start

    _PROJECT_ROOT = _find_project_root(_BASE)
    _SRC_PYTHON = _PROJECT_ROOT / "src" / "python"
    if str(_SRC_PYTHON) not in sys.path:
        sys.path.insert(0, str(_SRC_PYTHON))


    _HARMONIZED_DIR = "data/processed/sumstats_harmonized"
    _CLUMP_DIR = "data/processed/clumping"
    _AFR_PLINK = "data/reference/ldsc/1000G_AFR_Phase3_plink"
    _EUR_PLINK = "data/reference/ldsc/1000G_EUR_Phase3_plink"


    def _ldpop_for_ancestry(ancestry: str) -> str:
        """Map cell ancestry to LD reference population.

        D-M2-Q3: TRANS/MULTI uses EUR primary (RESEARCH Q4 default).
        D-M2-02: AFR uses 1000G_AFR_Phase3_plink built in Wave 0 Task 4.
        """
        if ancestry == "EUR":
            return "EUR"
        if ancestry == "AFR":
            return "AFR"
        if ancestry in ("TRANS", "MULTI"):
            return "EUR"   # D-M2-Q3 + RESEARCH Q4 default
        if ancestry in ("EAS", "SAS", "HIS"):
            return "EUR"   # cross-ancestry approximation; documented as M3-supersede candidate
        raise ValueError(f"Unknown ancestry: {ancestry}")


    rule m2_plink_clump_per_chr:
        """Per-(trait × ancestry × chr) PLINK 1.9 --clump.

        Filters: --clump-p1 5e-8 --clump-p2 1 --clump-r2 0.01 --clump-kb 1000 (D-M2-09).
        LD ref: 1000G_{EUR|AFR}_Phase3_plink per _ldpop_for_ancestry().
        Memory budget per Q3: 4000 MB (2.5x peak headroom for chr1).
        """
        input:
            sumstats=lambda wc: f"{_HARMONIZED_DIR}/{wc.trait}.{wc.ancestry}.{wc.consortium}.{wc.year}.GRCh37.tsv.bgz",
            bed=lambda wc: f"data/reference/ldsc/1000G_{_ldpop_for_ancestry(wc.ancestry)}_Phase3_plink/1000G.{_ldpop_for_ancestry(wc.ancestry)}.QC.{wc.chr}.bed",
        output:
            clumped=f"{_CLUMP_DIR}/{{ancestry}}/{{trait}}.{{ancestry}}.{{consortium}}.{{year}}.LD-1000G-{{ldpop}}.chr{{chr}}.clumped",
        params:
            bfile=lambda wc: f"data/reference/ldsc/1000G_{_ldpop_for_ancestry(wc.ancestry)}_Phase3_plink/1000G.{_ldpop_for_ancestry(wc.ancestry)}.QC.{wc.chr}",
            out_prefix=f"{_CLUMP_DIR}/{{ancestry}}/{{trait}}.{{ancestry}}.{{consortium}}.{{year}}.LD-1000G-{{ldpop}}.chr{{chr}}",
        conda:
            "../../../envs/m2-clumping.yml"
        resources:
            mem_mb=4000,
            runtime=60,
        threads: 2
        shell:
            r"""
            set -euo pipefail
            mkdir -p $(dirname {params.out_prefix})

            # Decompress harmonized .tsv.bgz to a temp TSV with SNP + P columns for plink --clump
            TMP_TSV=$(mktemp --suffix=.tsv)
            trap "rm -f $TMP_TSV" EXIT
            zcat {input.sumstats} | head -1 > $TMP_TSV.header
            # Identify SNP and P column indices from header (handle column-name variants)
            SNP_COL=$(awk -F'\t' 'NR==1 {{ for(i=1;i<=NF;i++) if($i=="SNP" || $i=="rsid" || $i=="rsID") {{print i; exit}} }}' $TMP_TSV.header)
            P_COL=$(awk -F'\t' 'NR==1 {{ for(i=1;i<=NF;i++) if($i=="P" || $i=="p" || $i=="P_value" || $i=="pval") {{print i; exit}} }}' $TMP_TSV.header)
            if [ -z "$SNP_COL" ] || [ -z "$P_COL" ]; then
                echo "ERROR: could not identify SNP/P columns in {input.sumstats}" >&2
                cat $TMP_TSV.header >&2
                exit 1
            fi
            zcat {input.sumstats} | awk -v s=$SNP_COL -v p=$P_COL -F'\t' \
                'BEGIN{{OFS="\t"}} NR==1{{print "SNP","P"; next}} {{print $s, $p}}' \
                > $TMP_TSV

            plink \
                --bfile {params.bfile} \
                --clump $TMP_TSV \
                --clump-snp-field SNP \
                --clump-field P \
                --clump-p1 5e-8 \
                --clump-p2 1 \
                --clump-r2 0.01 \
                --clump-kb 1000 \
                --memory 3500 \
                --out {params.out_prefix}

            # Touch output even if no clumps (PLINK skips writing if empty per Q3)
            if [ ! -f {output.clumped} ]; then touch {output.clumped}; fi
            """


    rule m2_plink_clump_per_trait_ancestry:
        """Aggregator — concatenate all 22 chr clumped files into one BED per (trait × ancestry).

        Output BED schema: chr, start=BP-1, end=BP, name=SNP, score=., strand=.
        """
        input:
            chr_files=lambda wc: expand(
                f"{_CLUMP_DIR}/{{ancestry}}/{{trait}}.{{ancestry}}.{{consortium}}.{{year}}.LD-1000G-{{ldpop}}.chr{{chr}}.clumped",
                ancestry=[wc.ancestry], trait=[wc.trait], consortium=[wc.consortium],
                year=[wc.year], ldpop=[wc.ldpop], chr=range(1, 23),
            ),
        output:
            bed=f"{_CLUMP_DIR}/{{ancestry}}/{{trait}}.{{ancestry}}.{{consortium}}.{{year}}.LD-1000G-{{ldpop}}.clumped.bed",
        conda:
            "../../../envs/m2-regions.yml"
        resources:
            mem_mb=2000,
            runtime=10,
        shell:
            r"""
            set -euo pipefail
            python -c "
            import pandas as pd, sys
            chr_files = '''{input.chr_files}'''.split()
            rows = []
            for f in chr_files:
                try:
                    df = pd.read_csv(f, sep=r'\s+', engine='python')
                except Exception as e:
                    continue
                if df.empty or 'SNP' not in df.columns:
                    continue
                rows.append(df[['CHR', 'BP', 'SNP']].rename(columns={{'CHR':'chr','BP':'pos','SNP':'name'}}))
            if not rows:
                # No clumps — emit empty BED
                pd.DataFrame(columns=['chr','start','end','name','score','strand']).to_csv('{output.bed}', sep='\t', index=False, header=False)
                sys.exit(0)
            out = pd.concat(rows, ignore_index=True)
            out['chr'] = 'chr' + out['chr'].astype(str)
            out['start'] = out['pos'].astype(int) - 1
            out['end'] = out['pos'].astype(int)
            out['score'] = '.'
            out['strand'] = '.'
            out[['chr','start','end','name','score','strand']].to_csv('{output.bed}', sep='\t', index=False, header=False)
            print(f'Wrote {{len(out)}} lead variants to {output.bed}')
            "
            """
    ```

    Then add an aggregator rule `m2_clumping_all_active_cells` that uses m2_stratum_keys to enumerate the active (trait × ancestry) cells and expand into the per-trait-ancestry BED outputs.

    Production fire:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
        --use-conda \
        --snakefile src/snakemake/rules/m2_clumping.smk \
        --cores 16 \
        --resources mem_mb=64000 \
        m2_clumping_all_active_cells
    ```

    Update tests/m2/test_plink_clump_invocation.py from RED → GREEN — assert the rule's shell block contains the literal flags `--clump-p1 5e-8`, `--clump-r2 0.01`, `--clump-kb 1000`.

    Atomic commit: `feat(m2-04): m2_clumping.smk per-(trait × ancestry × chr) PLINK 1.9 clumping (D-M2-09, Pitfall 5)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f src/snakemake/rules/m2_clumping.smk &amp;&amp; grep -c -- "--clump-p1 5e-8" src/snakemake/rules/m2_clumping.smk &amp;&amp; grep -c -- "--clump-r2 0.01" src/snakemake/rules/m2_clumping.smk &amp;&amp; grep -c -- "--clump-kb 1000" src/snakemake/rules/m2_clumping.smk &amp;&amp; grep -c "rule m2_plink_clump_per_chr:" src/snakemake/rules/m2_clumping.smk &amp;&amp; grep -c "1000G_AFR_Phase3_plink" src/snakemake/rules/m2_clumping.smk &amp;&amp; grep -c "envs/m2-clumping.yml" src/snakemake/rules/m2_clumping.smk &amp;&amp; pytest tests/m2/test_plink_clump_invocation.py -x &amp;&amp; ls data/processed/clumping/EUR/*.clumped.bed | head -3</automated>
  </verify>
  <acceptance_criteria>
    - File `src/snakemake/rules/m2_clumping.smk` exists ≥80 lines
    - `grep -c -- "--clump-p1 5e-8" src/snakemake/rules/m2_clumping.smk` returns ≥1 (D-M2-09)
    - `grep -c -- "--clump-p2 1" src/snakemake/rules/m2_clumping.smk` returns ≥1 (D-M2-09)
    - `grep -c -- "--clump-r2 0.01" src/snakemake/rules/m2_clumping.smk` returns ≥1 (D-M2-09)
    - `grep -c -- "--clump-kb 1000" src/snakemake/rules/m2_clumping.smk` returns ≥1 (D-M2-09)
    - `grep -c "1000G_AFR_Phase3_plink" src/snakemake/rules/m2_clumping.smk` returns ≥1 (D-M2-02)
    - `grep -c "1000G_EUR_Phase3_plink" src/snakemake/rules/m2_clumping.smk` returns ≥1
    - `grep -c "envs/m2-clumping.yml" src/snakemake/rules/m2_clumping.smk` returns ≥1
    - `grep -c -- "plink2 " src/snakemake/rules/m2_clumping.smk` returns 0 (Pitfall 5 — only PLINK 1.9)
    - `pytest tests/m2/test_plink_clump_invocation.py -x` exits 0
    - After production fire: at least 5 `.clumped.bed` files exist at `data/processed/clumping/EUR/`
    - For at least one EUR cell: the .clumped.bed file has > 10 rows (cardiometabolic traits at HM3 density yield many lead SNPs)
    - `git log --oneline -3 | grep "m2_clumping.smk"`
  </acceptance_criteria>
  <done>m2_clumping.smk authored with PLINK 1.9 invocation; D-M2-09 thresholds enforced literally; 1000G EUR + AFR LD reference paths wired correctly per ancestry; per-(trait × ancestry) clumped BED files land for active cells; ROADMAP success criterion 4 input ready.</done>
</task>

<task type="auto">
  <name>Task 2: select_mtcojo_eligible_targets.py + m2_mtcojo.smk + production fire (D-M2-08, D-M2-Q3, D-M2-Q5)</name>
  <files>src/python/select_mtcojo_eligible_targets.py, src/snakemake/rules/m2_mtcojo.smk, data/processed/mtcojo/{stratum}/, tests/m2/test_mtcojo_eligible_targets.py, tests/m2/test_mtcojo_extreme_overlap_filter.py</files>
  <read_first>
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Q4" lines 236-249 (mtCOJO TRANS LD reference choice)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Q8" lines 338-360 (mtCOJO output schema)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §D-M2-08 lines 106-112
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §D-M2-Q3 + §D-M2-Q5 lines 254-270
    - data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv (Wave 1 — provides gcov_int values per pair)
    - data/processed/ldsc_overlap/rg_matrix_long_M2.tsv (Wave 1 — long-form fat TSV consumed by the eligibility filter)
    - data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt (Wave 2)
    - envs/m2-mtcojo.yml (Wave 0 Task 2 — provides gcta=1.94)
    - tests/m2/test_mtcojo_eligible_targets.py + tests/m2/test_mtcojo_extreme_overlap_filter.py (RED stubs from Wave 0 Task 1)
  </read_first>
  <action>
    **Step A — `src/python/select_mtcojo_eligible_targets.py`:**

    ```python
    #!/usr/bin/env python3
    """Per-stratum eligible-target selector for mtCOJO sensitivity (D-M2-08 + D-M2-Q5).

    A (stratum, target_trait) tuple is eligible iff:
      1. MTAG produced a novel locus for target_trait in this stratum
         (mtag_pval < 5e-8 AND max_FDR < 0.05 in {stratum}_mtag_maxfdr_filtered.txt)
      2. The bivariate-intercept gcov_int between target_trait and ANY contributing
         covariate trait exceeds 0.1 (D-M2-08 threshold; Turley 2018 §"sample overlap")
    """
    from __future__ import annotations
    import argparse
    import json
    from pathlib import Path
    import pandas as pd

    _GCOV_INT_THRESHOLD = 0.1   # D-M2-08 Turley 2018 recommended


    def select_eligible_targets(
        mtag_filtered_path: Path,
        long_matrix_path: Path,
        sidecar_path: Path,
    ) -> pd.DataFrame:
        """Return DataFrame with columns [target_trait, max_overlapping_intercept, max_with_trait, n_mtag_novel_loci]."""
        # Read MTAG filtered output
        mtag = pd.read_csv(mtag_filtered_path, sep='\t')
        # Identify target trait column — MTAG output by default has columns SNP, CHR, BP, A1, A2, EAF, BETA_<trait>, SE_<trait>, P_<trait>, max_FDR
        # Per-trait novel locus count from columns matching pattern "P_<trait>"
        p_cols = [c for c in mtag.columns if c.startswith("P_") and not c.startswith("P_value")]
        novel_per_trait = {}
        for c in p_cols:
            trait_label = c[2:]  # strip "P_"
            n_novel = (mtag[c] < 5e-8).sum()
            novel_per_trait[trait_label] = int(n_novel)

        # Read long-form matrix for gcov_int per pair
        long = pd.read_csv(long_matrix_path, sep='\t')
        # Schema: trait_a, trait_b, rg, rg_se, gcov_int, gcov_int_se, h2_a, h2_b
        if 'gcov_int' not in long.columns:
            raise ValueError(f"Long matrix at {long_matrix_path} missing gcov_int column")

        # Read sidecar for canonical trait list in this stratum
        sidecar = json.loads(sidecar_path.read_text())
        stratum_traits = sidecar["trait_order"]

        # For each target_trait with mtag-novel count > 0, find max overlapping intercept
        rows = []
        for target in stratum_traits:
            n_novel = novel_per_trait.get(target, 0)
            if n_novel == 0:
                continue
            pairs = long[((long['trait_a'] == target) | (long['trait_b'] == target))]
            pairs = pairs[(pairs['trait_a'].isin(stratum_traits)) & (pairs['trait_b'].isin(stratum_traits))]
            pairs = pairs[(pairs['trait_a'] != pairs['trait_b'])]
            if pairs.empty:
                continue
            max_intercept = float(pairs['gcov_int'].abs().max())
            other_for_max = pairs.loc[pairs['gcov_int'].abs().idxmax()]
            other_trait = other_for_max['trait_b'] if other_for_max['trait_a'] == target else other_for_max['trait_a']
            if max_intercept > _GCOV_INT_THRESHOLD:
                rows.append({
                    "target_trait": target,
                    "max_overlapping_intercept": max_intercept,
                    "max_with_trait": other_trait,
                    "n_mtag_novel_loci": n_novel,
                })
        return pd.DataFrame(rows, columns=["target_trait", "max_overlapping_intercept", "max_with_trait", "n_mtag_novel_loci"])


    def _main() -> None:
        ap = argparse.ArgumentParser(description=__doc__)
        ap.add_argument("--stratum", required=True)
        ap.add_argument("--mtag-filtered", type=Path, required=True)
        ap.add_argument("--long-matrix", type=Path, required=True)
        ap.add_argument("--sidecar", type=Path, required=True)
        ap.add_argument("--out", type=Path, required=True)
        args = ap.parse_args()
        df = select_eligible_targets(args.mtag_filtered, args.long_matrix, args.sidecar)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.out, sep='\t', index=False)
        print(f"{args.stratum}: {len(df)} eligible target traits (gcov_int > {_GCOV_INT_THRESHOLD})")


    if __name__ == "__main__":
        _main()
    ```

    Wire tests/m2/test_mtcojo_eligible_targets.py + tests/m2/test_mtcojo_extreme_overlap_filter.py from RED → GREEN.

    **Step B — `src/snakemake/rules/m2_mtcojo.smk`:**

    ```python
    """M2 Wave 4 — mtCOJO sensitivity per (stratum, target_trait) per D-M2-08 + Q5.

    TRANS uses 1000G EUR LD primary + 1000G AFR sensitivity column (D-M2-Q3).
    """
    from pathlib import Path
    import os, sys

    try:
        _BASE = Path(workflow.basedir)  # type: ignore[name-defined]
    except NameError:
        _BASE = Path(os.getcwd())

    _MTAG_DIR = "data/processed/mtag"
    _MTCOJO_DIR = "data/processed/mtcojo"
    _LONG_MATRIX = "data/processed/ldsc_overlap/rg_matrix_long_M2.tsv"
    _HARMONIZED_DIR = "data/processed/sumstats_harmonized"

    STRATA = ("EUR", "AFR", "TRANS")


    def _mtcojo_ld_ref(stratum: str) -> str:
        """D-M2-Q3: TRANS uses EUR primary; Q4 sensitivity is run separately as a re-check."""
        if stratum == "EUR":
            return "data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC"
        if stratum == "AFR":
            return "data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC"
        if stratum == "TRANS":
            return "data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC"  # primary
        raise ValueError(stratum)


    rule m2_mtcojo_eligible_targets:
        """Per-stratum eligibility list (D-M2-Q5) — only MTAG-novel target traits with gcov_int > 0.1."""
        input:
            mtag_filtered=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_maxfdr_filtered.txt",
            long_matrix=_LONG_MATRIX,
            sidecar=f"{_MTAG_DIR}/{{stratum}}/residcov.trait_order.json",
        output:
            tsv=f"{_MTCOJO_DIR}/{{stratum}}/mtcojo_eligible_targets.tsv",
        conda:
            "../../../envs/m2-cpassoc.yml"
        shell:
            r"""
            mkdir -p $(dirname {output.tsv})
            python src/python/select_mtcojo_eligible_targets.py \
                --stratum {wildcards.stratum} \
                --mtag-filtered {input.mtag_filtered} \
                --long-matrix {input.long_matrix} \
                --sidecar {input.sidecar} \
                --out {output.tsv}
            """


    rule m2_mtcojo_run:
        """Per (stratum, target_trait) mtCOJO conditional analysis (D-M2-08).

        TRANS-stratum runs additionally with 1000G AFR LD as sensitivity per D-M2-Q3
        (handled in m2_mtcojo_aggregate_sensitivity rule downstream).
        """
        input:
            eligible=f"{_MTCOJO_DIR}/{{stratum}}/mtcojo_eligible_targets.tsv",
        output:
            cojo=f"{_MTCOJO_DIR}/{{stratum}}/{{trait}}.mtcojo.cojo",
            log=f"{_MTCOJO_DIR}/{{stratum}}/{{trait}}.mtcojo.log",
        params:
            ld_ref=lambda wc: _mtcojo_ld_ref(wc.stratum),
            out_prefix=f"{_MTCOJO_DIR}/{{stratum}}/{{trait}}.mtcojo",
        conda:
            "../../../envs/m2-mtcojo.yml"
        resources:
            mem_mb=8000,
            runtime=120,
        threads: 4
        shell:
            r"""
            set -euo pipefail
            # Build the mtcojo input list: target trait first, then covariate traits from sidecar
            INPUT_LIST=$(mktemp --suffix=.list)
            trap "rm -f $INPUT_LIST" EXIT
            python -c "
            import json, sys
            from pathlib import Path
            sidecar = json.loads(Path('{input.eligible}').parent.parent.joinpath('mtag/{wildcards.stratum}/residcov.trait_order.json').read_text())
            target = '{wildcards.trait}'
            others = [t for t in sidecar['trait_order'] if t != target]
            with open('$INPUT_LIST', 'w') as f:
                f.write(target + '\t{_HARMONIZED_DIR}/' + target + '.GRCh37.tsv.bgz\n')
                for t in others:
                    f.write(t + '\t{_HARMONIZED_DIR}/' + t + '.GRCh37.tsv.bgz\n')
            "
            cat $INPUT_LIST

            gcta \
                --bfile {params.ld_ref}.22 \
                --mtcojo-file $INPUT_LIST \
                --w-ld-chr data/external/ldscore/eur_w_ld_chr/ \
                --ref-ld-chr data/external/ldscore/eur_w_ld_chr/ \
                --out {params.out_prefix} \
                2>&1 | tee {output.log}
            test -s {output.cojo}
            """


    rule m2_mtcojo_sensitivity_table:
        """Aggregate per-stratum mtcojo outputs into one mtcojo_sensitivity.tsv per Q8 schema."""
        input:
            eligible=f"{_MTCOJO_DIR}/{{stratum}}/mtcojo_eligible_targets.tsv",
        output:
            sensitivity=f"{_MTCOJO_DIR}/{{stratum}}/mtcojo_sensitivity.tsv",
        conda:
            "../../../envs/m2-cpassoc.yml"
        shell:
            r"""
            python -c "
            import pandas as pd, glob
            from pathlib import Path
            elig = pd.read_csv('{input.eligible}', sep='\t')
            rows = []
            for _, r in elig.iterrows():
                target = r['target_trait']
                cojo_path = Path('{_MTCOJO_DIR}/{wildcards.stratum}/' + target + '.mtcojo.cojo')
                if not cojo_path.exists():
                    continue
                cojo = pd.read_csv(cojo_path, sep=r'\s+')
                # Schema per Q8: SNP, A1, A2, freq, b, se, p, N, b_cojo, se_cojo, p_cojo
                for _, c in cojo.iterrows():
                    p_cojo = c.get('p_cojo', None)
                    flag = 'PASS' if p_cojo is not None and p_cojo < 5e-8 else 'WARN' if p_cojo is not None and p_cojo < 1e-5 else 'FAIL'
                    rows.append({{
                        'locus_id': c.get('SNP', ''),
                        'trait': target,
                        'mtag_p_original': c.get('p', None),
                        'mtcojo_p': p_cojo,
                        'max_overlapping_intercept': r['max_overlapping_intercept'],
                        'sensitivity_flag': flag,
                    }})
            pd.DataFrame(rows).to_csv('{output.sensitivity}', sep='\t', index=False)
            "
            """
    ```

    Production fire:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
        --use-conda \
        --snakefile src/snakemake/rules/m2_mtcojo.smk \
        --cores 8 \
        --resources mem_mb=24000 \
        $(for s in EUR AFR TRANS; do echo "data/processed/mtcojo/$s/mtcojo_sensitivity.tsv"; done)
    ```

    Atomic commit: `feat(m2-04): m2_mtcojo.smk + select_mtcojo_eligible_targets.py + production fire (D-M2-08, D-M2-Q3, D-M2-Q5)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f src/python/select_mtcojo_eligible_targets.py &amp;&amp; test -f src/snakemake/rules/m2_mtcojo.smk &amp;&amp; grep -c "_GCOV_INT_THRESHOLD = 0.1" src/python/select_mtcojo_eligible_targets.py &amp;&amp; grep -c "rule m2_mtcojo_eligible_targets:" src/snakemake/rules/m2_mtcojo.smk &amp;&amp; grep -c "rule m2_mtcojo_run:" src/snakemake/rules/m2_mtcojo.smk &amp;&amp; grep -c "rule m2_mtcojo_sensitivity_table:" src/snakemake/rules/m2_mtcojo.smk &amp;&amp; pytest tests/m2/test_mtcojo_eligible_targets.py tests/m2/test_mtcojo_extreme_overlap_filter.py -x &amp;&amp; ls data/processed/mtcojo/EUR/mtcojo_eligible_targets.tsv 2>/dev/null || echo "fire not yet complete"</automated>
  </verify>
  <acceptance_criteria>
    - File `src/python/select_mtcojo_eligible_targets.py` exists ≥60 lines
    - `grep -c "_GCOV_INT_THRESHOLD = 0.1" src/python/select_mtcojo_eligible_targets.py` returns 1 (D-M2-08)
    - File `src/snakemake/rules/m2_mtcojo.smk` exists ≥80 lines
    - `grep -c "rule m2_mtcojo_eligible_targets:" src/snakemake/rules/m2_mtcojo.smk` returns 1
    - `grep -c "rule m2_mtcojo_run:" src/snakemake/rules/m2_mtcojo.smk` returns 1
    - `grep -c "rule m2_mtcojo_sensitivity_table:" src/snakemake/rules/m2_mtcojo.smk` returns 1
    - `grep -c "1000G_EUR_Phase3_plink" src/snakemake/rules/m2_mtcojo.smk` returns ≥1 (D-M2-Q3 TRANS uses EUR primary)
    - `grep -c "gcta " src/snakemake/rules/m2_mtcojo.smk` returns ≥1
    - `grep -c "envs/m2-mtcojo.yml" src/snakemake/rules/m2_mtcojo.smk` returns ≥1
    - `pytest tests/m2/test_mtcojo_eligible_targets.py tests/m2/test_mtcojo_extreme_overlap_filter.py -x` exits 0
    - After fire: at least one stratum's `data/processed/mtcojo/{stratum}/mtcojo_eligible_targets.tsv` exists
    - At least one stratum's `data/processed/mtcojo/{stratum}/mtcojo_sensitivity.tsv` exists with header `locus_id\ttrait\tmtag_p_original\tmtcojo_p\tmax_overlapping_intercept\tsensitivity_flag` (Q8 schema)
    - `git log --oneline -3 | grep "m2_mtcojo"`
  </acceptance_criteria>
  <done>m2_mtcojo.smk + select_mtcojo_eligible_targets.py both authored; D-M2-08 gcov_int>0.1 filter enforced; D-M2-Q3 TRANS uses EUR LD primary; D-M2-Q5 only MTAG-novel targets fire mtCOJO; sensitivity table emits Q8 schema; ROADMAP success criterion 6 satisfied.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: build_region_union.py + m2_regions.smk + production fire — strict union BED with provenance JSON (D-M2-09, Q6, Pitfall 9)</name>
  <files>src/python/build_region_union.py, src/snakemake/rules/m2_regions.smk, results/regions/union_region_list.bed, tests/m2/test_build_region_union.py</files>
  <read_first>
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Q6" lines 291-310 (full schema + bedtools default merge contract)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Pitfall 9" lines 647-655 (no -s flag for genomic regions)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §D-M2-09 lines 114-125
    - data/processed/clumping/{ancestry}/*.clumped.bed (Task 1 output — clumped lead BEDs)
    - data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt (Wave 2 — MTAG-novel leads)
    - data/processed/cpassoc/{stratum}/cpassoc_results.tsv (Wave 3 — CPASSOC-novel leads)
    - envs/m2-regions.yml (Wave 0 Task 2 — provides bedtools=2.31.1)
    - tests/m2/test_build_region_union.py (RED stub from Wave 0 Task 1)
  </read_first>
  <behavior>
    build_region_union(clumped_beds, mtag_filtered_paths, cpassoc_results_paths, out_path):
      1. Read all clumped BEDs → DataFrame [chr, pos, name, source='clump', stratum]
      2. Extract MTAG-novel lead BPs from each filtered output: rows with mtag_pval < 5e-8 AND max_FDR < 0.05; pick lead per ±1 Mb LD-block within each (stratum, trait) → DataFrame with source='mtag'
      3. Extract CPASSOC-novel lead BPs: rows with SHom_p < 5e-8 OR SHet_p < 5e-8; pick lead per ±1 Mb → DataFrame with source='cpassoc'
      4. Union all three DataFrames; build ±1 Mb windows per lead: start = max(0, pos - 1_000_000); end = pos + 1_000_000
      5. Sort by chr, start; emit a sorted-input BED to bedtools merge
      6. Run bedtools merge with NO -d, NO -s flags (Q6 + Pitfall 9 — strict default)
      7. For each merged region: collect contributing leads' provenance and emit a JSON column listing {clump: [trait_strata], mtag: [strata], cpassoc: [strata]}
      8. Write results/regions/union_region_list.bed with columns chr, start, end, region_id, score=., strand=., provenance_json
  </behavior>
  <action>
    **Step A — `src/python/build_region_union.py`:**

    ```python
    #!/usr/bin/env python3
    """Build genome-wide union region BED from clumped + MTAG-novel + CPASSOC-novel leads.

    Plan: m2-04-clumping-mtcojo-regions-PLAN.md.
    Decisions: D-M2-09 (strict union, ±1 Mb windows, provenance JSON column).
    Q6: bedtools default merge (no -d, no -s — Pitfall 9).
    Expected ~1500-3000 merged regions per amendment text.
    """
    from __future__ import annotations
    import argparse
    import json
    import subprocess
    from pathlib import Path
    import pandas as pd

    _WINDOW_BP = 1_000_000   # ±1 Mb per D-M2-09


    def _extract_clumped_leads(clumped_beds: list[Path]) -> pd.DataFrame:
        rows = []
        for f in clumped_beds:
            if not f.exists() or f.stat().st_size == 0:
                continue
            df = pd.read_csv(f, sep='\t', header=None,
                             names=['chr','start','end','name','score','strand'])
            # Filename pattern: {trait}.{ancestry}.{consortium}.{year}.LD-1000G-{ldpop}.clumped.bed
            stem = f.stem.replace('.clumped', '')
            parts = stem.split('.')
            trait, ancestry = parts[0], parts[1]
            df['source'] = 'clump'
            df['stratum'] = ancestry
            df['trait'] = trait
            df['pos'] = df['end']
            rows.append(df[['chr','pos','name','source','stratum','trait']])
        if not rows:
            return pd.DataFrame(columns=['chr','pos','name','source','stratum','trait'])
        return pd.concat(rows, ignore_index=True)


    def _extract_mtag_novel_leads(mtag_paths: list[Path]) -> pd.DataFrame:
        rows = []
        for f in mtag_paths:
            if not f.exists():
                continue
            df = pd.read_csv(f, sep='\t')
            # MTAG output schema includes CHR, BP, max_FDR + per-trait P_ columns
            stratum = f.parent.name
            p_cols = [c for c in df.columns if c.startswith('P_')]
            for c in p_cols:
                trait = c[2:]
                novel = df[df[c] < 5e-8]
                if 'max_FDR' in novel.columns:
                    novel = novel[novel['max_FDR'] < 0.05]
                if novel.empty:
                    continue
                novel = novel.copy()
                novel['source'] = 'mtag'
                novel['stratum'] = stratum
                novel['trait'] = trait
                novel = novel.rename(columns={'CHR':'chr','BP':'pos','SNP':'name'})
                rows.append(novel[['chr','pos','name','source','stratum','trait']])
        if not rows:
            return pd.DataFrame(columns=['chr','pos','name','source','stratum','trait'])
        return pd.concat(rows, ignore_index=True)


    def _extract_cpassoc_novel_leads(cpassoc_paths: list[Path]) -> pd.DataFrame:
        rows = []
        for f in cpassoc_paths:
            if not f.exists():
                continue
            df = pd.read_csv(f, sep='\t')
            stratum = f.parent.name
            novel = df[(df['SHom_p'] < 5e-8) | (df['SHet_p'] < 5e-8)].copy()
            if novel.empty:
                continue
            novel['source'] = 'cpassoc'
            novel['stratum'] = stratum
            novel['trait'] = 'joint'
            novel = novel.rename(columns={'rsid':'name'})
            rows.append(novel[['chr','pos','name','source','stratum','trait']])
        if not rows:
            return pd.DataFrame(columns=['chr','pos','name','source','stratum','trait'])
        return pd.concat(rows, ignore_index=True)


    def _normalize_chr(c) -> str:
        s = str(c).strip()
        if s.startswith('chr'):
            return s
        return f'chr{s}'


    def build_union(
        clumped_beds: list[Path],
        mtag_paths: list[Path],
        cpassoc_paths: list[Path],
        out_path: Path,
    ) -> int:
        clump_df = _extract_clumped_leads(clumped_beds)
        mtag_df = _extract_mtag_novel_leads(mtag_paths)
        cpassoc_df = _extract_cpassoc_novel_leads(cpassoc_paths)
        all_leads = pd.concat([clump_df, mtag_df, cpassoc_df], ignore_index=True)
        if all_leads.empty:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text("")
            return 0
        all_leads['chr'] = all_leads['chr'].apply(_normalize_chr)
        all_leads['pos'] = all_leads['pos'].astype(int)
        all_leads['start'] = (all_leads['pos'] - _WINDOW_BP).clip(lower=0)
        all_leads['end'] = all_leads['pos'] + _WINDOW_BP

        # Write windowed BED (sorted) for bedtools merge
        windowed_bed = out_path.with_suffix('.windowed.bed')
        all_leads.sort_values(['chr','start','end'], inplace=True)
        all_leads[['chr','start','end','name','source','stratum','trait']].to_csv(
            windowed_bed, sep='\t', index=False, header=False
        )

        # bedtools merge with default settings (Q6 + Pitfall 9 — no -d, no -s)
        merged_bed = out_path.with_suffix('.merged.bed')
        subprocess.run(
            ['bedtools', 'merge', '-i', str(windowed_bed),
             '-c', '4,5,6,7', '-o', 'collapse,collapse,collapse,collapse'],
            check=True, stdout=open(merged_bed, 'w'),
        )

        # Build provenance JSON per region
        merged = pd.read_csv(merged_bed, sep='\t', header=None,
                             names=['chr','start','end','names','sources','strata','traits'])
        out_rows = []
        for i, r in merged.iterrows():
            sources = r['sources'].split(',')
            strata = r['strata'].split(',')
            traits = r['traits'].split(',')
            prov = {'clump': [], 'mtag': [], 'cpassoc': []}
            for s, st, t in zip(sources, strata, traits):
                key = s if s in prov else 'clump'
                prov[key].append(f'{t}.{st}')
            for k in prov:
                prov[k] = sorted(set(prov[k]))
            out_rows.append({
                'chr': r['chr'],
                'start': r['start'],
                'end': r['end'],
                'region_id': f'm2_region_{i+1:05d}',
                'score': '.',
                'strand': '.',
                'provenance_json': json.dumps(prov, separators=(',',':')),
            })
        out_df = pd.DataFrame(out_rows)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(out_path, sep='\t', index=False, header=False)
        return len(out_df)


    def _main() -> None:
        ap = argparse.ArgumentParser(description=__doc__)
        ap.add_argument('--clumped-beds', nargs='+', type=Path, required=True)
        ap.add_argument('--mtag-paths', nargs='+', type=Path, required=True)
        ap.add_argument('--cpassoc-paths', nargs='+', type=Path, required=True)
        ap.add_argument('--out', type=Path, required=True)
        args = ap.parse_args()
        n = build_union(args.clumped_beds, args.mtag_paths, args.cpassoc_paths, args.out)
        print(f'Wrote {n} merged regions to {args.out}')


    if __name__ == '__main__':
        _main()
    ```

    **Step B — `src/snakemake/rules/m2_regions.smk`:**

    ```python
    """M2 Wave 4 — region union BED builder per D-M2-09."""
    from pathlib import Path
    import os, sys

    try:
        _BASE = Path(workflow.basedir)  # type: ignore[name-defined]
    except NameError:
        _BASE = Path(os.getcwd())

    _CLUMP_DIR = "data/processed/clumping"
    _MTAG_DIR = "data/processed/mtag"
    _CPASSOC_DIR = "data/processed/cpassoc"
    _REGIONS_OUT = "results/regions/union_region_list.bed"

    STRATA = ("EUR", "AFR", "TRANS")


    rule m2_build_region_union:
        """Strict union BED of clumped + MTAG-novel + CPASSOC-novel leads (D-M2-09, Q6).

        bedtools default merge (no -d, no -s — Pitfall 9). ±1 Mb windows per lead.
        Output schema: chr, start, end, region_id, score=., strand=., provenance_json
        """
        input:
            clumped=lambda wc: [str(p) for p in Path(_CLUMP_DIR).rglob("*.clumped.bed")],
            mtag=expand(f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_maxfdr_filtered.txt", stratum=STRATA),
            cpassoc=expand(f"{_CPASSOC_DIR}/{{stratum}}/cpassoc_results.tsv", stratum=STRATA),
        output:
            bed=_REGIONS_OUT,
        conda:
            "../../../envs/m2-regions.yml"
        resources:
            mem_mb=8000,
            runtime=30,
        shell:
            r"""
            mkdir -p $(dirname {output.bed})
            python src/python/build_region_union.py \
                --clumped-beds {input.clumped} \
                --mtag-paths {input.mtag} \
                --cpassoc-paths {input.cpassoc} \
                --out {output.bed}
            wc -l {output.bed}
            """
    ```

    Production fire:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
        --use-conda \
        --snakefile src/snakemake/rules/m2_regions.smk \
        --cores 4 \
        m2_build_region_union
    ```

    Wire tests/m2/test_build_region_union.py from RED → GREEN.

    Atomic commit: `feat(m2-04): build_region_union.py + m2_regions.smk + production fire (D-M2-09, Q6, Pitfall 9)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f src/python/build_region_union.py &amp;&amp; test -f src/snakemake/rules/m2_regions.smk &amp;&amp; grep -c "_WINDOW_BP = 1_000_000" src/python/build_region_union.py &amp;&amp; grep -c "bedtools.*merge" src/python/build_region_union.py &amp;&amp; grep -c "rule m2_build_region_union:" src/snakemake/rules/m2_regions.smk &amp;&amp; pytest tests/m2/test_build_region_union.py -x &amp;&amp; test -s results/regions/union_region_list.bed &amp;&amp; wc -l results/regions/union_region_list.bed</automated>
  </verify>
  <acceptance_criteria>
    - File `src/python/build_region_union.py` exists ≥100 lines
    - `grep -c "_WINDOW_BP = 1_000_000" src/python/build_region_union.py` returns 1 (±1 Mb per D-M2-09)
    - `grep -c "bedtools.*merge" src/python/build_region_union.py` returns ≥1
    - `grep -c -- "-s " src/python/build_region_union.py` returns 0 (Pitfall 9 — no strand-aware merge)
    - File `src/snakemake/rules/m2_regions.smk` exists
    - `grep -c "rule m2_build_region_union:" src/snakemake/rules/m2_regions.smk` returns 1
    - `pytest tests/m2/test_build_region_union.py -x` exits 0
    - After fire: file `results/regions/union_region_list.bed` exists with > 100 rows (lower bound — amendment expects 1,500-3,000 but we accept > 100 to allow for sparser-than-expected discovery)
    - First column of every row begins with `chr`
    - Last column is parseable JSON: `awk -F'\t' '{print $NF}' results/regions/union_region_list.bed | head -3 | python -c "import json, sys; [json.loads(l) for l in sys.stdin]"`
    - Provenance JSON contains keys `clump`, `mtag`, `cpassoc`
    - `git log -1 --pretty=%B` matches `feat(m2-04): build_region_union.py`
  </acceptance_criteria>
  <done>build_region_union.py + m2_regions.smk authored; results/regions/union_region_list.bed produced via strict bedtools default merge (Q6 + Pitfall 9 enforced); provenance JSON per region; ROADMAP success criterion 4 satisfied; M3 hand-off region list frozen.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Harmonized .tsv.bgz → PLINK --clump input | Column-name detection (SNP/rsid; P/p/pval) is heuristic; AWK sniff should never fail in production |
| 1000G AFR PLINK bfile (Wave 0 build) → m2_clumping.smk input | Wave 0 Task 4 BLOCKING dependency; Snakemake fails closed if missing |
| MTAG output schema → eligible-target selector | P_<trait>, max_FDR columns must exist; the selector's parser is robust to column-name variation |
| bedtools merge defaults → "strict union" | Q6 confirms `-d` default = 0 (any overlap); Pitfall 9 reminds NOT to use `-s` |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M2-06 | Tampering | PLINK 2.0 silently lacks --clump | mitigate | envs/m2-clumping.yml pins plink=1.9 (Wave 0 Task 2); rule grep tests assert no `plink2 ` invocations |
| T-M2-07 | Information disclosure | mtCOJO LD reference mismatch (TRANS) | mitigate | _mtcojo_ld_ref returns 1000G EUR for TRANS per D-M2-Q3; sensitivity check (1000G AFR) is a planned Wave 4 robustness add |
| T-M2-08 | Tampering | bedtools merge tolerance off-by-one | mitigate | Default merge (no -d) per Q6; pytest test_build_region_union covers strict-union semantics |
| T-M2-PITFALL-9 | Tampering | -s flag accidentally enabled (no merging happens) | mitigate | grep test asserts no `-s ` argument in build_region_union.py shell calls |
| T-M2-AFR-PLINK-MISSING | DoS | 1000G AFR PLINK bfile not yet built | mitigate | Snakemake input dependency on m2_reference.smk fails closed; Wave 0 Task 4 sign-off blocks Wave 4 fire |
</threat_model>

<verification>
End-of-Wave-4 verifier checks:

```bash
set -e
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

# Module + rule files exist
test -f src/snakemake/rules/m2_clumping.smk
test -f src/snakemake/rules/m2_mtcojo.smk
test -f src/snakemake/rules/m2_regions.smk
test -f src/python/build_region_union.py
test -f src/python/select_mtcojo_eligible_targets.py

# CRITICAL — plink=1.9 not plink2 (Pitfall 5)
! grep -E "plink2 " src/snakemake/rules/m2_clumping.smk

# CRITICAL — no strand-aware merge (Pitfall 9)
! grep -E -- "-s " src/python/build_region_union.py

# Region union BED produced
test -s results/regions/union_region_list.bed
N=$(wc -l < results/regions/union_region_list.bed)
test "$N" -gt 100
echo "Union BED: $N regions"

# Provenance JSON parseable
awk -F'\t' '{print $NF}' results/regions/union_region_list.bed | head -3 | python -c "import json, sys; [json.loads(l) for l in sys.stdin]"

# At least one stratum has mtcojo_sensitivity.tsv
ls data/processed/mtcojo/*/mtcojo_sensitivity.tsv | wc -l | awk '{exit !($1 >= 1)}'

# Tests
pytest tests/m2/test_plink_clump_invocation.py tests/m2/test_mtcojo_eligible_targets.py tests/m2/test_mtcojo_extreme_overlap_filter.py tests/m2/test_build_region_union.py -x

echo "Wave 4 PASS"
```
</verification>

<success_criteria>
- src/snakemake/rules/m2_clumping.smk exists; D-M2-09 thresholds (5e-8, 1, 0.01, 1000) literally present
- 1000G AFR PLINK bfile path wired; 1000G EUR for TRANS (D-M2-Q3)
- src/python/select_mtcojo_eligible_targets.py + src/snakemake/rules/m2_mtcojo.smk exist; gcov_int > 0.1 filter (D-M2-08); only MTAG-novel targets fire mtCOJO (D-M2-Q5); TRANS uses EUR LD primary (D-M2-Q3)
- src/python/build_region_union.py + src/snakemake/rules/m2_regions.smk exist; bedtools default merge (Q6 + Pitfall 9); ±1 Mb windows; provenance JSON column
- Production fire complete: clumped BEDs, mtcojo_sensitivity.tsv, results/regions/union_region_list.bed all land
- Region count > 100 (lower bound; amendment expects 1,500-3,000)
- ROADMAP success criteria 4 + 6 satisfied
- All commits atomic per task; convention `feat|data(m2-04): <summary>`
</success_criteria>

<output>
After completion, create `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-04-SUMMARY.md` documenting:
- Total clumped lead-variant count per (trait × ancestry × stratum)
- Total MTAG-novel lead count per stratum (post-max_FDR filter)
- Total CPASSOC-novel lead count per stratum
- Final union region count (target: 1500-3000 per amendment)
- mtCOJO eligible target count per stratum
- Any TRANS-stratum mtCOJO concordance with the 1000G AFR sensitivity check (D-M2-Q3)
- LSF wall time per task
</output>
