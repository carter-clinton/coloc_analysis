#!/usr/bin/env bash
# Fire MTAG for all 3 strata (EUR, AFR, TRANS) in parallel.
#
# Plan: m2-02-mtag-3-strata Task 4.
#
# Bypasses Snakemake --use-conda env build (which had stale-prefix issues
# in this session) by invoking the patched MTAG directly via the existing
# magma_helpers conda env at .snakemake/conda/23976dd9637257af71fe0dc567fc580a_/
# (numpy=1.26.4 + pandas=2.2.1 + joblib pip-installed).
#
# The Snakemake rule m2_mtag_run is the canonical production driver; this
# fire script is the CLI surface for the M2 Wave 2 production fire that
# matches the Snakemake rule's argv exactly.
#
# Decisions exercised:
#   D-M2-03  — three strata (EUR, AFR, TRANS)
#   D-M2-07  — --p_sig 5e-8 (genome-wide significance)
#   D-M2-Q1  — --fdr (post-hoc max-FDR computation)
#   D-M2-10  — --residcov_path (NOT --overlap; verified literal)
#
# Pitfalls navigated:
#   Pitfall 1  — never --overlap; always --residcov_path
#   Pitfall 2  — residcov.txt is bare-numeric (already verified Wave 2 Task 3)
#   Pitfall 6  — vendored MTAG runs against numpy=1.26 (Pitfall 6 ABI lock)
#   Pitfall 7  — sidecar trait_order.json drives --sumstats list ordering

set -euo pipefail
cd "$(dirname "$0")/.."  # repo root

PY=.snakemake/conda/23976dd9637257af71fe0dc567fc580a_/bin/python
MTAG_REPO=tools/mtag
MUNGED_DIR=data/processed/mtag/munged_for_mtag
MTAG_DIR=data/processed/mtag

export PYTHONPATH=$MTAG_REPO:${PYTHONPATH:-}

fire_stratum() {
    local stratum=$1
    local out_dir=$MTAG_DIR/$stratum
    local out_prefix=$out_dir/${stratum}_mtag
    local log=$out_dir/${stratum}_mtag_run.log

    # Build --sumstats list from sidecar trait order (Pitfall 7)
    local SUMSTATS_LIST
    SUMSTATS_LIST=$(/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -c "
import json
ord_list = json.load(open('$out_dir/residcov.trait_order.json'))['trait_order']
paths = ['$MUNGED_DIR/' + k + '.sumstats.gz' for k in ord_list]
print(','.join(paths))
")
    local TRAIT_ORDER
    TRAIT_ORDER=$(/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -c "import json; print(','.join(json.load(open('$out_dir/residcov.trait_order.json'))['trait_order']))")

    {
        echo "===== Stratum $stratum ====="
        echo "Trait order: $TRAIT_ORDER"
        echo "Sumstats list: $SUMSTATS_LIST"
        echo "Residcov path: $out_dir/residcov.txt (--residcov_path; D-M2-10 corrected)"
        echo "Output prefix: $out_prefix"
        echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } | tee "$log"

    $PY $MTAG_REPO/mtag.py \
        --sumstats "$SUMSTATS_LIST" \
        --residcov_path "$out_dir/residcov.txt" \
        --out "$out_prefix" \
        --snp_name SNP --a1_name A1 --a2_name A2 \
        --n_name N --z_name Z --p_name P --eaf_name FRQ \
        --no_chr_data \
        --p_sig 5e-8 \
        --n_min 0 --maf_min 0.01 \
        --fdr \
        --stream_stdout \
        2>&1 | tee -a "$log"

    echo "Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$log"
}

# Fire all 3 strata in parallel
echo "Firing 3 strata in parallel — EUR/AFR/TRANS"
fire_stratum EUR > /dev/null 2>&1 &
PID_EUR=$!
fire_stratum AFR > /dev/null 2>&1 &
PID_AFR=$!
fire_stratum TRANS > /dev/null 2>&1 &
PID_TRANS=$!

echo "PIDs: EUR=$PID_EUR AFR=$PID_AFR TRANS=$PID_TRANS"

wait $PID_EUR && echo "EUR done" || echo "EUR FAILED"
wait $PID_AFR && echo "AFR done" || echo "AFR FAILED"
wait $PID_TRANS && echo "TRANS done" || echo "TRANS FAILED"

echo "All fires finished — checking outputs"
for s in EUR AFR TRANS; do
    if [ -f $MTAG_DIR/$s/${s}_mtag_trait_1.txt ]; then
        echo "$s: trait_1.txt OK ($(wc -l < $MTAG_DIR/$s/${s}_mtag_trait_1.txt) lines)"
    else
        echo "$s: MISSING trait_1.txt"
    fi
done
