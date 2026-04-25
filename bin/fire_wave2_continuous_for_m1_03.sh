#!/usr/bin/env bash
# bin/fire_wave2_continuous_for_m1_03.sh — m1-03 deviation: fire Wave 2a
# continuous-trait harmonizers that were authored in m1-02a but never
# production-fired. Required because m1-03 needs harmonized inputs to
# munge into LDSC .sumstats.gz format.
#
# Skips:
#   - Loh×2 BMI EUR/AFR — DEFERRED per m1-01 N1 (D-01 unresolved)
#   - MAGIC HbA1c EUR — DEFERRED per DEF-M1-02a-01 (truncated raw file)
#   - DIAMANTE×4 — Wave 2b territory; cookie-pending
#   - GBMI×3 — Wave 2b territory; portal-pending
#
# Fires (1 + 15 + 3 + 1 + 5 = 25 jobs):
#   - Yengo BMI EUR (already fired by inline call above)
#   - PAGE BMI AFR (1)
#   - GLGC × 15 (LDL × 6, HDL × 3, TG × 3, TC × 3)
#   - Wuttke eGFR TRANS / EUR + Morris eGFR AFR (3)
#   - MAGIC HbA1c TRANS / AFR / EAS / SAS / HIS (5; EUR skipped — DEF-M1-02a-01)
#
# Usage: bash bin/fire_wave2_continuous_for_m1_03.sh [PARALLEL]
#   PARALLEL: xargs -P parallelism (default 5; HPC cooperative)

set -euo pipefail

PARALLEL="${1:-5}"
SMOKE_PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
export PATH=/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin:$PATH  # bgzip + tabix

HARM=data/processed/sumstats_harmonized
PARQ=data/processed/sumstats_harmonized_parquet
QC=data/processed/sumstats_harmonized/qc_log
RAW=data/raw/sumstats_v2

mkdir -p "$HARM" "$PARQ" "$QC"

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

JOB_LOG="$WORK/jobs.tsv"
: > "$JOB_LOG"

# ---------------------------------------------------------------------------
# Helper: register a harmonize call (script, args, output basename).
# ---------------------------------------------------------------------------
add_job() {
    local outname="$1"; shift
    local script="$1"; shift
    # remaining args = python script invocation args (after --output, --parquet, --qc-json)
    if [ -f "$HARM/$outname.GRCh37.tsv.bgz" ] && [ -s "$HARM/$outname.GRCh37.tsv.bgz" ]; then
        echo "SKIP  $outname (already on disk)" >&2
        return
    fi
    echo -e "${outname}\t${script}\t$*" >> "$JOB_LOG"
}

# ---------------------------------------------------------------------------
# Yengo / Loh / PAGE BMI
# ---------------------------------------------------------------------------
add_job bmi.EUR.GIANT-UKBB.2018 src/python/harmonize_yengo.py \
    --input "$RAW/GIANT2018/BMI/EUR/Meta-analysis_Locke_et_al+UKBiobank_2018_UPDATED.txt.gz" \
    --variant yengo2018 --trait bmi --ancestry EUR --consortium GIANT-UKBB --year 2018

add_job bmi.AFR.PAGE.2019 src/python/harmonize_yengo.py \
    --input "$RAW/PAGE2019/BMI/AFR/WojcikG_PMID_invn_rbmi_alls.gz" \
    --variant page2019_afr --trait bmi --ancestry AFR --consortium PAGE --year 2019

# ---------------------------------------------------------------------------
# GLGC × 15
# ---------------------------------------------------------------------------
glgc_one() {
    local lipid_uc=$1 lipid_lc=$2 ancestry=$3
    local rawdir="$RAW/GLGC2021/${lipid_uc}/${ancestry}"
    local raw=$(ls "$rawdir"/*.gz 2>/dev/null | head -1)
    if [ -z "$raw" ]; then
        echo "SKIP  ${lipid_lc}.${ancestry}.GLGC.2021 (no raw file)" >&2
        return
    fi
    add_job ${lipid_lc}.${ancestry}.GLGC.2021 src/python/harmonize_glgc.py \
        --input "$raw" \
        --subtype "$lipid_uc" --ancestry "$ancestry" --consortium GLGC --year 2021
}

for ANC in TRANS EUR AFR EAS SAS HIS; do glgc_one LDL ldl "$ANC"; done
for ANC in TRANS EUR AFR; do glgc_one HDL hdl "$ANC"; done
for ANC in TRANS EUR AFR; do glgc_one TG  tg  "$ANC"; done
for ANC in TRANS EUR AFR; do glgc_one TC  tc  "$ANC"; done

# ---------------------------------------------------------------------------
# Wuttke / Morris eGFR
# ---------------------------------------------------------------------------
wuttke_one() {
    local variant=$1 ancestry=$2
    local rawdir="$RAW/CKDGen2019/eGFR/${ancestry}"
    local raw=$(ls "$rawdir"/*.gz 2>/dev/null | head -1)
    if [ -z "$raw" ]; then
        echo "SKIP  egfr.${ancestry}.CKDGen.2019 (no raw file)" >&2
        return
    fi
    add_job egfr.${ancestry}.CKDGen.2019 src/python/harmonize_wuttke.py \
        --input "$raw" \
        --variant "$variant" --ancestry "$ancestry" --consortium CKDGen --year 2019
}

wuttke_one wuttke2019_trans TRANS
wuttke_one wuttke2019_eur   EUR
wuttke_one morris2019_afr   AFR

# ---------------------------------------------------------------------------
# MAGIC HbA1c (skip EUR — DEF-M1-02a-01 truncation)
# ---------------------------------------------------------------------------
magic_one() {
    local ancestry=$1
    local rawdir="$RAW/MAGIC2021/HbA1c/${ancestry}"
    local raw=$(ls "$rawdir"/*.gz 2>/dev/null | head -1)
    if [ -z "$raw" ]; then
        echo "SKIP  hba1c.${ancestry}.MAGIC.2021 (no raw file)" >&2
        return
    fi
    add_job hba1c.${ancestry}.MAGIC.2021 src/python/harmonize_magic.py \
        --input "$raw" \
        --ancestry "$ancestry" --consortium MAGIC --year 2021
}

for ANC in TRANS AFR EAS SAS HIS; do magic_one "$ANC"; done

# ---------------------------------------------------------------------------
# Worker function (executes one job line; sorts + bgzips + tabixes the output).
# ---------------------------------------------------------------------------
echo "Job queue ($(wc -l < "$JOB_LOG") jobs):"
cat "$JOB_LOG" | awk -F'\t' '{print "  ", $1}'

cat > "$WORK/worker.sh" <<'WORKER_EOF'
#!/usr/bin/env bash
set -eo pipefail
SMOKE_PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
export PATH=/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin:$PATH
HARM=data/processed/sumstats_harmonized
PARQ=data/processed/sumstats_harmonized_parquet
QC=data/processed/sumstats_harmonized/qc_log

OUTNAME="$1"; SCRIPT="$2"; shift 2
ARGS=("$@")
TMP=$(mktemp --tmpdir="${TMPDIR:-/tmp}" "${OUTNAME}.XXXXX.tsv.gz")
PRE_SORT_OUT="${HARM}/${OUTNAME}.GRCh37.unsorted.tsv.gz"

START=$(date +%s)
$SMOKE_PY "$SCRIPT" \
    "${ARGS[@]}" \
    --output "$PRE_SORT_OUT" \
    --parquet "$PARQ/${OUTNAME}.GRCh37.parquet" \
    --qc-json "$QC/${OUTNAME}.qc.json"

# Sort + bgzip + tabix
(zcat "$PRE_SORT_OUT" | head -1; zcat "$PRE_SORT_OUT" | tail -n +2 | sort -k1,1n -k2,2n) | bgzip -c > "$HARM/${OUTNAME}.GRCh37.tsv.bgz"
tabix -s 1 -b 2 -e 2 -S 1 -f "$HARM/${OUTNAME}.GRCh37.tsv.bgz"
rm -f "$PRE_SORT_OUT" "$TMP"

END=$(date +%s)
echo "DONE  ${OUTNAME}  ($(($END - $START))s)"
WORKER_EOF
chmod +x "$WORK/worker.sh"

# ---------------------------------------------------------------------------
# xargs -P PARALLEL dispatch.
# ---------------------------------------------------------------------------
N_JOBS=$(wc -l < "$JOB_LOG")
echo "Firing $N_JOBS jobs with -P $PARALLEL parallelism..."
START_TS=$(date +%s)

awk -F'\t' '{print $0}' "$JOB_LOG" | while IFS=$'\t' read -r outname script rest; do
    # Re-quote args so xargs receives one job per line
    printf "%s\t%s\t%s\n" "$outname" "$script" "$rest"
done > "$WORK/jobs_quoted.tsv"

set +e
cat "$WORK/jobs_quoted.tsv" | xargs -P "$PARALLEL" -I {} bash -c '
    line="{}"
    # split on tab
    outname=$(echo "$line" | cut -f1)
    script=$(echo "$line" | cut -f2)
    rest=$(echo "$line" | cut -f3-)
    bash "'"$WORK/worker.sh"'" "$outname" "$script" $rest
' 2>&1 | tee "$WORK/run.log"
RC=$?
set -e

END_TS=$(date +%s)
WALL=$(( END_TS - START_TS ))
echo
echo "Wave 2a fire complete. Wall: ${WALL}s. Exit code: $RC"
echo "Outputs:"
ls "$HARM"/*.GRCh37.tsv.bgz 2>/dev/null | xargs -n1 basename | sort | sed 's/^/  /'
