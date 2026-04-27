"""M2 Wave 4 — Per-(trait × ancestry × chr) PLINK 1.9 clumping.

Plan: m2-04-clumping-mtcojo-regions-PLAN.md.
Decisions:
  D-M2-09 — clump thresholds: --clump-p1 5e-8 --clump-p2 1 --clump-r2 0.01 --clump-kb 1000
  D-M2-02 — provisional 1000G AFR LD; M3-supersede commitment
  D-M2-Q3 — TRANS uses 1000G EUR primary (RESEARCH Q4 default; AFR is sensitivity check)
Pitfall 5 (m2-RESEARCH.md): PLINK 2.0 has NO --clump command.
  envs/m2-clumping.yml pins plink=1.9. NEVER plink2.

LD references (per ancestry):
  EUR cells   → data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC.{chr} (M1 staged)
  AFR cells   → data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{chr} (Wave 0 Task 4)
  TRANS cells → 1000G EUR primary per D-M2-Q3 + RESEARCH Q4

Inputs: harmonized .tsv.bgz at data/processed/sumstats_harmonized/{trait}.{ancestry}.{consortium}.{year}.GRCh37.tsv.bgz
Output: per-(trait × ancestry × chr) clumped text files; per-(trait × ancestry) aggregator BED
"""
from pathlib import Path
import os
import sys

try:
    _BASE = Path(workflow.basedir)  # type: ignore[name-defined]
except NameError:
    _BASE = Path(os.getcwd())


def _find_project_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(6):
        if (cur / "config" / "trait_inventory.yaml").is_file():
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

    D-M2-Q3 + RESEARCH Q4: TRANS/MULTI uses EUR primary.
    D-M2-02: AFR uses 1000G_AFR_Phase3_plink built in Wave 0 Task 4.
    Cross-ancestry approximation for EAS/SAS/HIS uses EUR (M3-supersede candidate).
    """
    if ancestry == "EUR":
        return "EUR"
    if ancestry == "AFR":
        return "AFR"
    if ancestry in ("TRANS", "MULTI"):
        return "EUR"   # D-M2-Q3 + RESEARCH Q4 default
    if ancestry in ("EAS", "SAS", "HIS"):
        return "EUR"   # cross-ancestry approximation; M3-supersede candidate
    raise ValueError(f"Unknown ancestry: {ancestry}")


# Active (trait × ancestry × consortium × year × ldpop) cell enumeration helper.
# Reads config/trait_inventory.yaml at rule-resolution time and emits the aggregator
# input list. The full enumeration is exposed via m2_clumping_all_active_cells below.
def _active_clumping_cells(inventory_path: Path = Path("config/trait_inventory.yaml")):
    import yaml as _yaml
    with open(inventory_path) as f:
        inv = _yaml.safe_load(f)
    cells_dict = inv.get("traits", inv) if isinstance(inv, dict) else {}
    out = []
    for key, entry in cells_dict.items():
        if not isinstance(entry, dict):
            continue
        if entry.get("qc_status") == "MISSING":
            continue
        harm = entry.get("harmonized_path", "")
        munged = entry.get("munged_path", "")
        if not harm or not munged:
            continue
        if not Path(harm).exists():
            continue
        ancestry = entry.get("ancestry", "")
        try:
            ldpop = _ldpop_for_ancestry(ancestry)
        except ValueError:
            continue
        out.append({
            "trait": entry.get("trait"),
            "ancestry": ancestry,
            "consortium": entry.get("consortium"),
            "year": entry.get("year"),
            "ldpop": ldpop,
            "harmonized_path": harm,
        })
    return out


rule m2_plink_clump_per_chr:
    """Per-(trait × ancestry × chr) PLINK 1.9 --clump.

    Filters (D-M2-09 literal): --clump-p1 5e-8 --clump-p2 1 --clump-r2 0.01 --clump-kb 1000.
    LD ref: 1000G_{EUR|AFR}_Phase3_plink per _ldpop_for_ancestry().
    Memory budget: 4000 MB (2.5x peak headroom for chr1).
    """
    input:
        sumstats=lambda wc: f"{_HARMONIZED_DIR}/{wc.trait}.{wc.ancestry}.{wc.consortium}.{wc.year}.GRCh37.tsv.bgz",
        bed=lambda wc: f"data/reference/ldsc/1000G_{wc.ldpop}_Phase3_plink/1000G.{wc.ldpop}.QC.{wc.chr}.bed",
    output:
        clumped=f"{_CLUMP_DIR}/{{ancestry}}/{{trait}}.{{ancestry}}.{{consortium}}.{{year}}.LD-1000G-{{ldpop}}.chr{{chr}}.clumped",
    params:
        bfile=lambda wc: f"data/reference/ldsc/1000G_{wc.ldpop}_Phase3_plink/1000G.{wc.ldpop}.QC.{wc.chr}",
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
        SNP_COL=$(awk -F'\t' 'NR==1 {{ for(i=1;i<=NF;i++) if($i=="SNP" || $i=="rsid" || $i=="rsID" || $i=="SNP_ID" || $i=="snp_id") {{print i; exit}} }}' $TMP_TSV.header)
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

        # Touch output even if no clumps (PLINK skips writing if empty)
        if [ ! -f {output.clumped} ]; then touch {output.clumped}; fi
        """


rule m2_plink_clump_per_trait_ancestry:
    """Aggregator — concatenate all 22 chr clumped files into one BED per (trait × ancestry).

    Output BED schema: chr, start=BP-1, end=BP, name=SNP, score=., strand=.
    Lead SNPs become 1bp BED entries; ±1 Mb windows applied at union step.
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
            except Exception:
                continue
            if df is None or df.empty or 'SNP' not in df.columns:
                continue
            rows.append(df[['CHR', 'BP', 'SNP']].rename(columns={{'CHR':'chr','BP':'pos','SNP':'name'}}))
        if not rows:
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


rule m2_clumping_all_active_cells:
    """Aggregator over all active (trait × ancestry) cells.

    Input enumeration is materialized at rule-resolution time from
    config/trait_inventory.yaml via _active_clumping_cells().
    """
    input:
        beds=lambda wc: [
            f"{_CLUMP_DIR}/{c['ancestry']}/{c['trait']}.{c['ancestry']}.{c['consortium']}.{c['year']}.LD-1000G-{c['ldpop']}.clumped.bed"
            for c in _active_clumping_cells()
        ],
    output:
        sentinel=f"{_CLUMP_DIR}/.m2_clumping_complete",
    shell:
        "touch {output.sentinel}"
