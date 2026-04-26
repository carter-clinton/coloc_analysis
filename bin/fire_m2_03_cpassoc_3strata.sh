#!/bin/bash
# Fire CPASSOC for all 3 strata (EUR, AFR, TRANS).
#
# Plan: m2-03-cpassoc-3-strata-PLAN.md Task 3.
#
# Production driver bypassing snakemake --use-conda env build (mamba reports
# "Non-conda folder exists at prefix - aborting" for envs/m2-cpassoc.yml; same
# stale-prefix issue documented in m2-02 Deviation #5). Uses the existing
# magma_helpers env at .snakemake/conda/23976dd9637257af71fe0dc567fc580a_/
# (numpy=1.26.4 + scipy=1.11.4 + pandas=2.2.1 — versions match m2-cpassoc.yml
# requirements verbatim). Invocation argv mirrors src/snakemake/rules/m2_cpassoc.smk
# rule m2_cpassoc_run shell block exactly so a future --use-conda re-fire
# produces byte-identical output.
#
# Wall: ~10-30 min per stratum; runs all 3 strata in parallel via background jobs.

set -euo pipefail

cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

PYBIN=".snakemake/conda/23976dd9637257af71fe0dc567fc580a_/bin/python"
MATRIX="data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv"
MUNGED_DIR="data/processed/mtag/munged_for_mtag"
MTAG_DIR="data/processed/mtag"
CPASSOC_DIR="data/processed/cpassoc"

mkdir -p "$CPASSOC_DIR"

fire_stratum() {
    local stratum="$1"
    local out_dir="$CPASSOC_DIR/$stratum"
    mkdir -p "$out_dir"
    local sidecar="$MTAG_DIR/$stratum/residcov.trait_order.json"
    local upstream_skip="$MTAG_DIR/$stratum/skipped_strata.tsv"
    local results="$out_dir/cpassoc_results.tsv"
    local log="$out_dir/cpassoc_run.log"

    echo "=== Firing CPASSOC for $stratum ==="

    # D-M2-Q6 cascade-skip guard.
    if [ -f "$upstream_skip" ]; then
        cp "$upstream_skip" "$out_dir/skipped_strata.tsv"
        echo "SKIPPED — upstream MTAG was below _MIN_PER_STRATUM=3 floor (D-M2-Q6 cascade)" \
            > "$log"
        printf "chr\tpos\trsid\tA1\tA2\tn_traits\tSHom_stat\tSHom_p\tSHet_stat\tSHet_p\tcontributing_traits\n" \
            > "$results"
        return 0
    fi

    # Fire CPASSOC.
    "$PYBIN" src/python/run_cpassoc.py \
        --stratum "$stratum" \
        --matrix "$MATRIX" \
        --mtag-sidecar "$sidecar" \
        --munged-dir "$MUNGED_DIR" \
        --out "$results" \
        2>&1 | tee "$log"

    test -s "$results"
    echo "=== Done $stratum: $(wc -l < "$results") rows ==="
}

# Fire 3 strata in parallel.
mkdir -p logs
fire_stratum EUR > logs/m2_03_cpassoc_EUR.out 2>&1 &
PID_EUR=$!
fire_stratum AFR > logs/m2_03_cpassoc_AFR.out 2>&1 &
PID_AFR=$!
fire_stratum TRANS > logs/m2_03_cpassoc_TRANS.out 2>&1 &
PID_TRANS=$!

echo "PIDs: EUR=$PID_EUR AFR=$PID_AFR TRANS=$PID_TRANS"

wait $PID_EUR
EUR_RC=$?
wait $PID_AFR
AFR_RC=$?
wait $PID_TRANS
TRANS_RC=$?

echo ""
echo "=== Exit codes ==="
echo "EUR=$EUR_RC AFR=$AFR_RC TRANS=$TRANS_RC"

if [ "$EUR_RC" -ne 0 ] || [ "$AFR_RC" -ne 0 ] || [ "$TRANS_RC" -ne 0 ]; then
    echo "ERROR: at least one stratum failed; check logs/m2_03_cpassoc_*.out"
    exit 1
fi

echo ""
echo "=== Per-stratum row counts + GWS hit counts ==="
for stratum in EUR AFR TRANS; do
    results="$CPASSOC_DIR/$stratum/cpassoc_results.tsv"
    if [ -f "$results" ]; then
        n_rows=$(wc -l < "$results")
        # 1 header + N data rows
        echo "$stratum: $((n_rows - 1)) data rows"
        "$PYBIN" -c "
import pandas as pd
df = pd.read_csv('$results', sep='\t')
gws_shom = (df['SHom_p'] < 5e-8).sum() if 'SHom_p' in df.columns else 0
gws_shet = (df['SHet_p'] < 5e-8).sum() if 'SHet_p' in df.columns else 0
print(f'  $stratum SHom GWS (p<5e-8): {gws_shom} / {len(df)}')
print(f'  $stratum SHet GWS (p<5e-8): {gws_shet} / {len(df)}')
"
    fi
done

echo "=== fire_m2_03_cpassoc_3strata.sh complete ==="
