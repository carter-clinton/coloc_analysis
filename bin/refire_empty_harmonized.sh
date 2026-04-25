#!/usr/bin/env bash
# bin/refire_empty_harmonized.sh — serially re-fire harmonizers whose
# output file has only the header row. Caused by a race in the prior
# xargs -P parallel fire on large GLGC TRANS Bayes-factor files; a serial
# pattern avoids the issue entirely.
set -euo pipefail

SMOKE_PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
export PATH=/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin:$PATH

HARM=data/processed/sumstats_harmonized
PARQ=data/processed/sumstats_harmonized_parquet
QC=data/processed/sumstats_harmonized/qc_log
RAW=data/raw/sumstats_v2

mkdir -p "$HARM" "$PARQ" "$QC"

run_one() {
    local outname="$1" script="$2"
    shift 2
    local out="$HARM/${outname}.GRCh37.tsv.bgz"
    local tmpunsorted="$HARM/${outname}.GRCh37.unsorted.tsv.gz"

    local nrows=$(zcat "$out" 2>/dev/null | wc -l)
    if [ "${nrows:-0}" -gt 1 ]; then
        echo "SKIP  $outname ($nrows rows)"
        return 0
    fi

    local s=$(date +%s)
    "$SMOKE_PY" "$script" "$@" \
        --output "$tmpunsorted" \
        --parquet "$PARQ/${outname}.GRCh37.parquet" \
        --qc-json "$QC/${outname}.qc.json"

    (zcat "$tmpunsorted" | head -1; zcat "$tmpunsorted" | tail -n +2 | sort -k1,1n -k2,2n) | bgzip -c > "$out"
    tabix -s 1 -b 2 -e 2 -S 1 -f "$out"
    rm -f "$tmpunsorted"
    local e=$(date +%s)
    echo "DONE  $outname  $((e - s))s  $(zcat "$out" | wc -l) rows"
}

# PAGE BMI AFR
run_one bmi.AFR.PAGE.2019 src/python/harmonize_yengo.py \
    --input "$RAW/PAGE2019/BMI/AFR/WojcikG_PMID_invn_rbmi_alls.gz" \
    --variant page2019_afr --trait bmi --ancestry AFR --consortium PAGE --year 2019

# Wuttke eGFR
WUTTKE_TRANS_RAW="$RAW/CKDGen2019/eGFR/TRANS/20171016_MW_eGFR_overall_ALL_nstud61.dbgap.txt.gz"
WUTTKE_EUR_RAW="$RAW/CKDGen2019/eGFR/EUR/20171017_MW_eGFR_overall_EA_nstud42.dbgap.txt.gz"
[ -f "$WUTTKE_TRANS_RAW" ] && run_one egfr.TRANS.CKDGen.2019 src/python/harmonize_wuttke.py \
    --input "$WUTTKE_TRANS_RAW" --variant wuttke2019_trans --ancestry TRANS --consortium CKDGen --year 2019
[ -f "$WUTTKE_EUR_RAW" ] && run_one egfr.EUR.CKDGen.2019 src/python/harmonize_wuttke.py \
    --input "$WUTTKE_EUR_RAW" --variant wuttke2019_eur --ancestry EUR --consortium CKDGen --year 2019

# GLGC × 15
glgc_one() {
    local lipid_uc=$1 lipid_lc=$2 ancestry=$3
    local rawdir="$RAW/GLGC2021/${lipid_uc}/${ancestry}"
    local raw=$(ls "$rawdir"/*.gz 2>/dev/null | head -1)
    [ -z "$raw" ] && { echo "SKIP  ${lipid_lc}.${ancestry}.GLGC.2021 (no raw)"; return; }
    run_one ${lipid_lc}.${ancestry}.GLGC.2021 src/python/harmonize_glgc.py \
        --input "$raw" --subtype "$lipid_uc" --ancestry "$ancestry" --consortium GLGC --year 2021
}

for ANC in TRANS EUR AFR EAS SAS HIS; do glgc_one LDL ldl "$ANC"; done
for ANC in TRANS EUR AFR; do glgc_one HDL hdl "$ANC"; done
for ANC in TRANS EUR AFR; do glgc_one TG  tg  "$ANC"; done
for ANC in TRANS EUR AFR; do glgc_one TC  tc  "$ANC"; done

echo
echo "Final harmonized inventory:"
ls "$HARM"/*.GRCh37.tsv.bgz 2>/dev/null | xargs -n1 basename | sort | sed 's/^/  /'
