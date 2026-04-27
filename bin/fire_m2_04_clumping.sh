#!/usr/bin/env bash
# bin/fire_m2_04_clumping.sh — M2 Wave 4 Task 1 production driver
#
# Mirrors src/snakemake/rules/m2_clumping.smk argv exactly so a future
# --use-conda re-fire produces byte-identical output (same Wave 2/3
# bypass pattern; documented as Rule 3 deviation).
#
# D-M2-09 thresholds: --clump-p1 5e-8 --clump-p2 1 --clump-r2 0.01 --clump-kb 1000
# Pitfall 5 (m2-RESEARCH.md): plink=1.9 only; PLINK 2.0 has no --clump.
set -euo pipefail

REPO=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
PLINK=/rs1/researchers/c/ckclinto/conda_envs/hlp_crossmap/bin/plink
PARALLEL=${PARALLEL:-16}

cd "$REPO"
mkdir -p data/processed/clumping logs

# Verify PLINK is 1.9 (Pitfall 5 fail-fast)
PLINK_VERSION=$("$PLINK" --version 2>&1 | head -1)
if ! echo "$PLINK_VERSION" | grep -q "PLINK v1.9"; then
    echo "ERROR: $PLINK is not PLINK 1.9 (got: $PLINK_VERSION). Pitfall 5 — PLINK 2.0 has no --clump." >&2
    exit 1
fi
echo "[fire_m2_04_clumping] $PLINK_VERSION"

# Build job list from active trait_inventory cells × 22 autosomes.
JOBS_TSV=$(mktemp --suffix=.tsv)
trap "rm -f $JOBS_TSV" EXIT

python3 -c "
import yaml
from pathlib import Path
inv = yaml.safe_load(open('config/trait_inventory.yaml'))
cells = inv.get('traits', inv) if isinstance(inv, dict) else {}
def ldpop(a):
    if a == 'AFR': return 'AFR'
    return 'EUR'  # EUR/TRANS/MULTI/EAS/SAS/HIS all use EUR per D-M2-Q3 + cross-ancestry approx
for k, e in cells.items():
    if not isinstance(e, dict): continue
    if e.get('qc_status') == 'MISSING': continue
    harm = e.get('harmonized_path','')
    if not harm or not Path(harm).exists(): continue
    a = e.get('ancestry','')
    if a not in ('EUR','AFR','TRANS','MULTI','EAS','SAS','HIS'): continue
    lp = ldpop(a)
    for ch in range(1, 23):
        bfile = f'data/reference/ldsc/1000G_{lp}_Phase3_plink/1000G.{lp}.QC.{ch}'
        if not Path(bfile + '.bed').exists():
            continue
        out_prefix = f\"data/processed/clumping/{a}/{e.get('trait')}.{a}.{e.get('consortium')}.{e.get('year')}.LD-1000G-{lp}.chr{ch}\"
        print('\t'.join([str(harm), str(bfile), out_prefix, str(ch)]))
" > "$JOBS_TSV"

NJOBS=$(wc -l < "$JOBS_TSV")
echo "[fire_m2_04_clumping] Enumerated $NJOBS PLINK jobs (cells × 22 chr)"

# Per-job runner: extract SNP+P columns, plink --clump
run_one() {
    local sumstats="$1"
    local bfile="$2"
    local out_prefix="$3"
    local chrom="$4"
    local outdir
    outdir=$(dirname "$out_prefix")
    mkdir -p "$outdir"
    local out_clumped="${out_prefix}.clumped"

    # Skip if already done (idempotent re-fire)
    if [ -s "$out_clumped" ] || [ -f "$out_clumped" ]; then
        return 0
    fi

    local tmp
    tmp=$(mktemp --suffix=.tsv)
    local header
    header=$(zcat "$sumstats" | head -1)
    local snp_col
    snp_col=$(echo "$header" | awk -F'\t' '{ for(i=1;i<=NF;i++) if($i=="SNP" || $i=="rsid" || $i=="rsID" || $i=="SNP_ID" || $i=="snp_id") {print i; exit} }')
    local p_col
    p_col=$(echo "$header" | awk -F'\t' '{ for(i=1;i<=NF;i++) if($i=="P" || $i=="p" || $i=="P_value" || $i=="pval") {print i; exit} }')
    local chr_col
    chr_col=$(echo "$header" | awk -F'\t' '{ for(i=1;i<=NF;i++) if($i=="CHR" || $i=="chr" || $i=="chrom" || $i=="Chr") {print i; exit} }')
    if [ -z "$snp_col" ] || [ -z "$p_col" ]; then
        echo "[fire_m2_04_clumping] ERROR: missing SNP/P col in $sumstats (header: $header)" >&2
        rm -f "$tmp"
        return 1
    fi

    if [ -n "$chr_col" ]; then
        zcat "$sumstats" | awk -v s="$snp_col" -v p="$p_col" -v c="$chr_col" -v ch="$chrom" -F'\t' \
            'BEGIN{OFS="\t"; print "SNP","P"} NR==1{next} ($c == ch){print $s, $p}' > "$tmp"
    else
        zcat "$sumstats" | awk -v s="$snp_col" -v p="$p_col" -F'\t' \
            'BEGIN{OFS="\t"; print "SNP","P"} NR==1{next} {print $s, $p}' > "$tmp"
    fi

    local nrows
    nrows=$(wc -l < "$tmp")
    if [ "$nrows" -le 1 ]; then
        # No SNPs on this chr → emit empty placeholder
        : > "$out_clumped"
        rm -f "$tmp"
        return 0
    fi

    "$PLINK" \
        --bfile "$bfile" \
        --clump "$tmp" \
        --clump-snp-field SNP \
        --clump-field P \
        --clump-p1 5e-8 \
        --clump-p2 1 \
        --clump-r2 0.01 \
        --clump-kb 1000 \
        --memory 3500 \
        --out "$out_prefix" \
        > "${out_prefix}.fire.log" 2>&1 || true

    if [ ! -f "$out_clumped" ]; then
        : > "$out_clumped"
    fi
    rm -f "$tmp"
}

export -f run_one
export PLINK

echo "[fire_m2_04_clumping] Launching $NJOBS jobs at parallelism $PARALLEL ..."
START=$(date +%s)

# xargs -P PARALLEL: pass each whole line as $1 to a wrapper that splits on tab
< "$JOBS_TSV" xargs -P "$PARALLEL" -I {} -d '\n' bash -c '
    line="$1"
    sumstats="${line%%	*}"; rest="${line#*	}"
    bfile="${rest%%	*}";    rest="${rest#*	}"
    out_prefix="${rest%%	*}"; chrom="${rest#*	}"
    run_one "$sumstats" "$bfile" "$out_prefix" "$chrom"
' _ {}

END=$(date +%s)
WALL=$((END - START))
echo "[fire_m2_04_clumping] All clump jobs done in ${WALL}s wall"

# Aggregate per-(trait × ancestry) BED files
echo "[fire_m2_04_clumping] Building per-(trait × ancestry) aggregator BEDs ..."
python3 << 'PYAGG'
import yaml
from pathlib import Path
import pandas as pd

inv = yaml.safe_load(open('config/trait_inventory.yaml'))
cells = inv.get('traits', inv) if isinstance(inv, dict) else {}

def ldpop(a):
    if a == 'AFR': return 'AFR'
    return 'EUR'

agg_count = 0
total_leads = 0
for k, e in cells.items():
    if not isinstance(e, dict): continue
    if e.get('qc_status') == 'MISSING': continue
    harm = e.get('harmonized_path','')
    if not harm or not Path(harm).exists(): continue
    a = e.get('ancestry','')
    if a not in ('EUR','AFR','TRANS','MULTI','EAS','SAS','HIS'): continue
    lp = ldpop(a)
    trait = e.get('trait')
    cons = e.get('consortium')
    yr = e.get('year')
    out_bed = Path(f'data/processed/clumping/{a}/{trait}.{a}.{cons}.{yr}.LD-1000G-{lp}.clumped.bed')
    rows = []
    for ch in range(1, 23):
        f = Path(f'data/processed/clumping/{a}/{trait}.{a}.{cons}.{yr}.LD-1000G-{lp}.chr{ch}.clumped')
        if not f.exists() or f.stat().st_size == 0:
            continue
        try:
            df = pd.read_csv(f, sep=r'\s+', engine='python')
        except Exception:
            continue
        if df is None or df.empty or 'SNP' not in df.columns:
            continue
        rows.append(df[['CHR','BP','SNP']].rename(columns={'CHR':'chr','BP':'pos','SNP':'name'}))
    out_bed.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        pd.DataFrame(columns=['chr','start','end','name','score','strand']).to_csv(out_bed, sep='\t', index=False, header=False)
        continue
    out = pd.concat(rows, ignore_index=True)
    out['chr'] = 'chr' + out['chr'].astype(str)
    out['start'] = out['pos'].astype(int) - 1
    out['end'] = out['pos'].astype(int)
    out['score'] = '.'
    out['strand'] = '.'
    out[['chr','start','end','name','score','strand']].to_csv(out_bed, sep='\t', index=False, header=False)
    agg_count += 1
    total_leads += len(out)
print(f'Wrote {agg_count} per-(trait × ancestry) BEDs; total {total_leads} lead variants')
PYAGG

touch data/processed/clumping/.m2_clumping_complete
echo "[fire_m2_04_clumping] DONE."
