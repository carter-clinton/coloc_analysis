#!/usr/bin/env bash
# bin/fire_m1_03_munge_and_rg.sh — m1-03 production fire driver.
#
# Stage 1: Munge every harmonized D-16 file under data/processed/sumstats_harmonized
#          into HM3-restricted .sumstats.gz under data/processed/ldsc_overlap/munged
#          (parallel via xargs -P).
# Stage 2: Build trait_keys.txt from the actually-munged files (NOT the
#          aspirational SUMSTATS-UPGRADE.tsv list — flexible per the plan's
#          autonomous instructions).
# Stage 3: Fire N-1 LDSC --rg star-topology calls in parallel, one log per
#          focal_idx, into data/processed/ldsc_overlap/rg_logs/.
# Stage 4: Reduce focal_*.log files into the NxN intercept matrix +
#          long-form TSV at data/processed/ldsc_overlap/.
#
# Usage:
#   bash bin/fire_m1_03_munge_and_rg.sh [STAGE]
#     STAGE = 1 | 2 | 3 | 4 | all (default: all)

set -euo pipefail

STAGE="${1:-all}"
PARALLEL_MUNGE="${PARALLEL_MUNGE:-6}"
PARALLEL_RG="${PARALLEL_RG:-22}"

SMOKE_PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
LDSC_PY=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.snakemake/conda/481e5f0b6ac97e63f5201cfab7469335_/bin/python
export PATH=/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin:$PATH

HARM=data/processed/sumstats_harmonized
MUNGED=data/processed/ldsc_overlap/munged
RG_LOGS=data/processed/ldsc_overlap/rg_logs
OVERLAP=data/processed/ldsc_overlap
HM3=data/external/ldscore/w_hm3.snplist
EUR_LD=data/external/ldscore/eur_w_ld_chr/
BIM_PREFIX=data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC

mkdir -p "$MUNGED" "$RG_LOGS" "$OVERLAP" logs

# ---------------------------------------------------------------------------
# Stage 1: Munge.
# ---------------------------------------------------------------------------
stage_munge() {
    echo "===== Stage 1: Munge harmonized files -> .sumstats.gz ====="
    local jobs_file
    jobs_file=$(mktemp)
    : > "$jobs_file"

    for harm_file in "$HARM"/*.GRCh37.tsv.bgz; do
        [ -f "$harm_file" ] || continue
        local base=$(basename "$harm_file" .GRCh37.tsv.bgz)
        local out="$MUNGED/${base}.sumstats.gz"
        if [ -f "$out" ] && [ -s "$out" ]; then
            echo "SKIP  munge ${base} (already present)"
            continue
        fi
        # Trait token is the leading dotted segment.
        local trait="${base%%.*}"
        printf "%s\t%s\t%s\n" "$harm_file" "$out" "$trait" >> "$jobs_file"
    done

    local n_jobs
    n_jobs=$(wc -l < "$jobs_file")
    echo "Munge queue: $n_jobs jobs"

    if [ "$n_jobs" -gt 0 ]; then
        local start=$(date +%s)
        cat "$jobs_file" | xargs -P "$PARALLEL_MUNGE" -I {} bash -c '
            line="{}"
            harm=$(echo "$line" | cut -f1)
            out=$(echo "$line" | cut -f2)
            trait=$(echo "$line" | cut -f3)
            base=$(basename "$out" .sumstats.gz)
            S=$(date +%s)
            echo "[munge] START $base"
            '"$SMOKE_PY"' src/python/munge_sumstats_ldsc.py \
                --input "$harm" \
                --output "$out" \
                --trait "$trait" \
                --merge-alleles '"$HM3"' \
                --chunksize 500000 \
                --bim-prefix '"$BIM_PREFIX"' \
                --ldsc-python '"$LDSC_PY"' \
                2>&1 | tail -3
            E=$(date +%s)
            echo "[munge] DONE  $base  ($((E-S))s)"
        '
        local end=$(date +%s)
        echo "Stage 1 wall: $((end - start))s"
    fi

    echo "Munged files on disk:"
    ls "$MUNGED"/*.sumstats.gz 2>/dev/null | wc -l
}

# ---------------------------------------------------------------------------
# Stage 2: Build trait_keys.txt from disk.
# ---------------------------------------------------------------------------
stage_trait_keys() {
    echo "===== Stage 2: Build trait_keys.txt from actually-munged files ====="
    ls "$MUNGED"/*.sumstats.gz 2>/dev/null \
        | xargs -n1 basename \
        | sed 's/\.sumstats\.gz$//' \
        | sort -u > "$OVERLAP/trait_keys.txt"
    echo "trait_keys.txt: $(wc -l < "$OVERLAP/trait_keys.txt") keys"
    cat "$OVERLAP/trait_keys.txt" | sed 's/^/  /'
}

# ---------------------------------------------------------------------------
# Stage 3: LDSC --rg star-topology fire.
# ---------------------------------------------------------------------------
stage_rg_stars() {
    echo "===== Stage 3: LDSC --rg star-topology fire ====="
    local n_keys
    n_keys=$(wc -l < "$OVERLAP/trait_keys.txt")
    if [ "$n_keys" -lt 2 ]; then
        echo "ERROR: need >=2 trait keys for any rg; have $n_keys"
        return 1
    fi
    local n_stars=$((n_keys - 1))
    echo "$n_keys traits -> $n_stars star calls (focal_0 through focal_$((n_stars - 1)))"

    # Compute parallel jobs from PAIR_WALL_SECONDS (Wave 0 Probe 3 emits 13).
    local pair_wall
    pair_wall=$(awk '/PAIR_WALL_SECONDS/ {print $2}' tests/m1/wave0_probes.log | head -1)
    if [ -z "$pair_wall" ]; then pair_wall=13; fi
    local jobs_p
    if [ "$pair_wall" -gt 1800 ]; then jobs_p=22; else jobs_p="$PARALLEL_RG"; fi
    echo "PAIR_WALL_SECONDS=$pair_wall -> --jobs $jobs_p (xargs -P $jobs_p)"

    local KEYS_ARR
    mapfile -t KEYS_ARR < "$OVERLAP/trait_keys.txt"
    local jobs_file
    jobs_file=$(mktemp)
    : > "$jobs_file"
    for ((i=0; i<n_stars; i++)); do
        local log="$RG_LOGS/focal_${i}.log"
        if [ -f "$log" ] && grep -q "Summary of Genetic Correlation Results" "$log" 2>/dev/null; then
            echo "SKIP  focal_${i} (existing log has Summary table)"
            continue
        fi
        printf "%s\n" "$i" >> "$jobs_file"
    done

    local n_to_fire
    n_to_fire=$(wc -l < "$jobs_file")
    echo "rg-star queue: $n_to_fire jobs"

    if [ "$n_to_fire" -gt 0 ]; then
        local start=$(date +%s)
        cat "$jobs_file" | xargs -P "$jobs_p" -I {} bash -c '
            i={}
            S=$(date +%s)
            mapfile -t KEYS < "'"$OVERLAP"'/trait_keys.txt"
            FOCAL="'"$MUNGED"'/${KEYS[$i]}.sumstats.gz"
            OTHERS=""
            for ((j=i+1; j<${#KEYS[@]}; j++)); do
                OTHERS+="${OTHERS:+,}'"$MUNGED"'/${KEYS[$j]}.sumstats.gz"
            done
            OUT_PREFIX="'"$RG_LOGS"'/focal_$i"
            echo "[rg-star] START focal_$i (focal=${KEYS[$i]}; vs $((${#KEYS[@]} - 1 - i)) others)"
            '"$LDSC_PY"' tools/ldsc/ldsc.py \
                --rg "$FOCAL,$OTHERS" \
                --ref-ld-chr '"$EUR_LD"' \
                --w-ld-chr   '"$EUR_LD"' \
                --out "$OUT_PREFIX" \
                > /dev/null 2>&1 || true
            E=$(date +%s)
            if grep -q "Summary of Genetic Correlation Results" "$OUT_PREFIX.log" 2>/dev/null; then
                STATUS=OK
            else
                STATUS=FAIL
            fi
            echo "[rg-star] DONE  focal_$i  ($((E-S))s) status=$STATUS"
        '
        local end=$(date +%s)
        echo "Stage 3 wall: $((end - start))s"
    fi

    echo "rg logs on disk:"
    ls "$RG_LOGS"/focal_*.log 2>/dev/null | wc -l
}

# ---------------------------------------------------------------------------
# Stage 4: Reduce.
# ---------------------------------------------------------------------------
stage_reduce() {
    echo "===== Stage 4: Reduce focal_*.log -> NxN matrix + long-form TSV ====="
    "$SMOKE_PY" src/python/reduce_ldsc_rg_matrix.py \
        --log-dir "$RG_LOGS" \
        --trait-keys-file "$OVERLAP/trait_keys.txt" \
        --output-matrix "$OVERLAP/bivariate_intercept_matrix_2026-04.tsv" \
        --output-long "$OVERLAP/rg_matrix_long.tsv" \
        --output-validation "$OVERLAP/rg_validation_warnings.json"
    echo
    echo "Validation warnings (rg_validation_warnings.json):"
    cat "$OVERLAP/rg_validation_warnings.json"
    echo
    echo "Matrix shape: $(awk 'NR==1{print NF-1, "cols"} END{print NR-1, "rows"}' "$OVERLAP/bivariate_intercept_matrix_2026-04.tsv")"
}

case "$STAGE" in
    1) stage_munge ;;
    2) stage_trait_keys ;;
    3) stage_rg_stars ;;
    4) stage_reduce ;;
    all)
        stage_munge
        stage_trait_keys
        stage_rg_stars
        stage_reduce
        ;;
    *) echo "Unknown stage: $STAGE"; exit 1 ;;
esac
