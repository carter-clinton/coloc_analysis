#!/usr/bin/env bash
# bin/fire_m2_04_mtcojo.sh — M2 Wave 4 Task 2 production driver
#
# Mirrors src/snakemake/rules/m2_mtcojo.smk argv exactly (Wave 2/3
# bypass pattern; documented as Rule 3 deviation).
#
# D-M2-08 + D-M2-Q5: only MTAG-novel target traits with extreme overlap
#                    (gcov_int > 0.1) fire mtCOJO.
# D-M2-Q3: TRANS uses 1000G EUR LD primary; AFR sensitivity is queued.
# CR-checker WR-4: m2_mtcojo_eligible_targets is a Snakemake CHECKPOINT
#                  in the smk file (commit 296f25d); this driver mirrors
#                  the checkpoint output by emitting eligible_targets.tsv
#                  THEN iterating only its rows for the per-target fires.
set -euo pipefail

REPO=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
GCTA=/rs1/researchers/c/ckclinto/conda_envs/gcta/bin/gcta-1.94.1
PYTHON=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python

cd "$REPO"
mkdir -p data/processed/mtcojo logs

START=$(date +%s)

for STRATUM in EUR AFR TRANS; do
    echo "[fire_m2_04_mtcojo] === Stratum: $STRATUM ==="
    OUTDIR="data/processed/mtcojo/$STRATUM"
    mkdir -p "$OUTDIR" "$OUTDIR/cojo_inputs"

    MTAG_FILT="data/processed/mtag/$STRATUM/${STRATUM}_mtag_maxfdr_filtered.txt"
    SIDECAR="data/processed/mtag/$STRATUM/residcov.trait_order.json"
    LONG="data/processed/ldsc_overlap/rg_matrix_long_M2.tsv"
    ELIG="$OUTDIR/mtcojo_eligible_targets.tsv"

    # Step 1: mtcojo_eligible_targets checkpoint
    echo "[fire_m2_04_mtcojo] $STRATUM: select eligible targets ..."
    PYTHONPATH="$REPO/src/python:${PYTHONPATH:-}" "$PYTHON" \
        "$REPO/src/python/select_mtcojo_eligible_targets.py" \
        --stratum "$STRATUM" \
        --mtag-filtered "$MTAG_FILT" \
        --long-matrix "$LONG" \
        --sidecar "$SIDECAR" \
        --out "$ELIG"

    # Step 2: per-target mtCOJO fires (over rows of $ELIG)
    if [ ! -s "$ELIG" ] || [ "$(wc -l < "$ELIG")" -le 1 ]; then
        echo "[fire_m2_04_mtcojo] $STRATUM: no eligible targets — skipping mtCOJO fires"
        # Still emit empty sensitivity table for downstream consumers
        "$PYTHON" "$REPO/src/python/build_mtcojo_sensitivity_table.py" \
            --stratum "$STRATUM" \
            --eligible "$ELIG" \
            --mtcojo-dir "$OUTDIR" \
            --mtag-filtered "$MTAG_FILT" \
            --out "$OUTDIR/mtcojo_sensitivity.tsv"
        continue
    fi

    # LD reference per stratum (D-M2-Q3)
    if [ "$STRATUM" = "AFR" ]; then
        LD_REF="data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC"
    else
        # EUR + TRANS both use 1000G EUR primary per D-M2-Q3
        LD_REF="data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC"
    fi
    LDSC_DIR="data/external/ldscore/eur_w_ld_chr"

    # Build mbfile (per-chr 1000G bfile prefixes)
    MBFILE="$OUTDIR/.mbfile"
    : > "$MBFILE"
    for c in $(seq 1 22); do
        BF="${LD_REF}.${c}"
        if [ -f "${BF}.bed" ]; then
            echo "${BF}" >> "$MBFILE"
        fi
    done

    while IFS=$'\t' read -r target rest; do
        if [ "$target" = "target_trait" ] || [ -z "$target" ]; then continue; fi
        echo "[fire_m2_04_mtcojo] $STRATUM/$target: building cojo inputs ..."
        PYTHONPATH="$REPO/src/python:${PYTHONPATH:-}" "$PYTHON" \
            "$REPO/src/python/build_cojo_inputs.py" \
            --target "$target" \
            --stratum "$STRATUM" \
            --sidecar "$SIDECAR" \
            --harmonized-dir "data/processed/sumstats_harmonized" \
            --out-dir "$OUTDIR/cojo_inputs" 2>&1 | tail -10

        echo "[fire_m2_04_mtcojo] $STRATUM/$target: running mtCOJO ..."
        OUT_PREFIX="$OUTDIR/${target}.mtcojo"
        LIST="$OUTDIR/cojo_inputs/${target}.mtcojo.list"
        "$GCTA" \
            --mtcojo-file "$LIST" \
            --mbfile "$MBFILE" \
            --w-ld-chr "$LDSC_DIR/" \
            --ref-ld-chr "$LDSC_DIR/" \
            --out "$OUT_PREFIX" \
            > "$OUT_PREFIX.fire.log" 2>&1 || {
                echo "[fire_m2_04_mtcojo] WARN: mtCOJO failed for $STRATUM/$target — see $OUT_PREFIX.fire.log"
                # Emit placeholder
                : > "$OUT_PREFIX.cojo"
            }
        # GCTA writes output file with .mtcojo.cma.cojo or similar — find the canonical one
        if [ ! -f "$OUT_PREFIX.cojo" ]; then
            # try several possible extensions
            for ext in .mtcojo.cma.cojo .cma.cojo .cma _cojo; do
                candidate="${OUT_PREFIX}${ext}"
                if [ -f "$candidate" ]; then
                    cp "$candidate" "$OUT_PREFIX.cojo"
                    break
                fi
            done
        fi
        if [ ! -f "$OUT_PREFIX.cojo" ]; then
            : > "$OUT_PREFIX.cojo"
        fi
    done < "$ELIG"

    # Step 3: aggregate sensitivity table
    echo "[fire_m2_04_mtcojo] $STRATUM: building sensitivity table ..."
    "$PYTHON" "$REPO/src/python/build_mtcojo_sensitivity_table.py" \
        --stratum "$STRATUM" \
        --eligible "$ELIG" \
        --mtcojo-dir "$OUTDIR" \
        --mtag-filtered "$MTAG_FILT" \
        --out "$OUTDIR/mtcojo_sensitivity.tsv"
done

END=$(date +%s)
echo "[fire_m2_04_mtcojo] DONE in $((END-START))s wall."
touch data/processed/mtcojo/.m2_mtcojo_complete
