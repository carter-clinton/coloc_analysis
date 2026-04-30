#!/usr/bin/env bash
# bin/fire_m2_post_m3_08_mtcojo.sh — M2-POST-M3-08 LSF burst-fire driver
#
# Closes obligation row M2-POST-M3-08 in
# .planning/m2_post_m3_rerun_queue.tsv:
#   "mtCOJO production sensitivity LSF re-fire for the 13 eligible
#    (target_trait, stratum) tuples with HM3-intersected COJO inputs"
#
# Mirrors src/snakemake/rules/m2_mtcojo.smk argv exactly (Wave 2/3
# bypass pattern; documented as Rule 3 deviation). The Snakemake rule
# remains canonical for re-discoverability — this driver is a bypass.
#
# Failure-mode addressed (witness:
# data/processed/mtcojo/EUR/bmi.EUR.GIANT-UKBB.2018.mtcojo.fire.log):
#   GCTA mtCOJO LDSC step terminates "no SNP in common between the
#   summary data and the LD score files". HM3 intersection of COJO
#   inputs upstream places GCTA's SNP namespace inside the
#   eur_w_ld_chr ld-score namespace.
#
# LSF resources (per m2_mtcojo.smk: mem_mb=8000, threads=4):
#   -q long                  → -W 14400 via config/bsub_wrapper.sh
#   -n 4                     → 4 cores
#   -R "rusage[mem=8]"       → 8 GB (LSF_UNIT_FOR_LIMITS=GB)
#
# Wall-time expectation: ~30 min per target × 13 targets, fully
# parallel on long queue → manifest delivered immediately.
set -euo pipefail

REPO=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
GCTA=/rs1/researchers/c/ckclinto/conda_envs/gcta/bin/gcta-1.94.1
PYTHON=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
HM3_SNPLIST=$REPO/tools/mtag/ld_ref_panel/eur_w_ld_chr/w_hm3.snplist
LDSC_DIR=$REPO/data/external/ldscore/eur_w_ld_chr
# Per-target output root: data/processed/mtcojo/<stratum>/m2p3_08/<target>/
# (unique per-target subdir to avoid clobbering legacy cojo_inputs/ from
# the failed first-pass fire — see build_cojo_inputs.py cache note.)

cd "$REPO"
mkdir -p logs/lsf data/processed/mtcojo

QUICK_DIR=".planning/quick/260429-s10-fire-m2-post-m3-08-mtcojo-production-sen"
mkdir -p "$QUICK_DIR"
BJOBS_TSV="$QUICK_DIR/bjobs.tsv"
BJOBS_COMMITTED="data/processed/mtcojo/m2_post_m3_08_bjobs.tsv"

# Manifest header
printf "submit_ts\tjob_id\tstratum\ttarget_trait\tld_ref\tjobscript\n" > "$BJOBS_TSV"

for STRATUM in EUR AFR TRANS; do
    ELIG="$REPO/data/processed/mtcojo/$STRATUM/mtcojo_eligible_targets.tsv"
    if [ ! -s "$ELIG" ]; then
        echo "[fire_m2_post_m3_08] WARN: no eligible_targets for $STRATUM — skipping"
        continue
    fi

    if [ "$STRATUM" = "AFR" ]; then
        LD_REF="data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC"
    else
        # EUR + TRANS both use 1000G EUR primary per D-M2-Q3
        LD_REF="data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC"
    fi

    tail -n +2 "$ELIG" | while IFS=$'\t' read -r TARGET _rest; do
        [ -z "$TARGET" ] && continue
        SHORT="${TARGET%%.*}"   # e.g. bmi.EUR.GIANT-UKBB.2018 → bmi
        JOBSCRIPT="logs/lsf/m2p3_08_${STRATUM}_${SHORT}.sh"

        # Render per-target jobscript with all REPO/PYTHON/GCTA/HM3_SNPLIST/LDSC_DIR
        # variables expanded at render time so the LSF jobscript is fully
        # self-contained (LSF compute hosts may have a different shell env).
        cat > "$JOBSCRIPT" <<EOF
#!/usr/bin/env bash
# Auto-rendered by bin/fire_m2_post_m3_08_mtcojo.sh
# Per-target LSF jobscript for M2-POST-M3-08 mtCOJO re-fire.
# Stratum: $STRATUM ; target: $TARGET
set -euo pipefail
cd "$REPO"

STRATUM="$STRATUM"
TARGET="$TARGET"
LD_REF="$LD_REF"

OUTDIR="data/processed/mtcojo/\$STRATUM/m2p3_08/\$TARGET"
mkdir -p "\$OUTDIR/cojo_inputs"

# Step 1: HM3-intersected COJO materialization
PYTHONPATH="$REPO/src/python:\${PYTHONPATH:-}" "$PYTHON" \\
    "$REPO/src/python/build_cojo_inputs.py" \\
    --target "\$TARGET" \\
    --stratum "\$STRATUM" \\
    --sidecar "data/processed/mtag/\$STRATUM/residcov.trait_order.json" \\
    --harmonized-dir "data/processed/sumstats_harmonized" \\
    --hm3-snplist "$HM3_SNPLIST" \\
    --out-dir "\$OUTDIR/cojo_inputs"

# Step 2: build mbfile from per-chr 1000G {EUR|AFR} bfiles
MBFILE="\$OUTDIR/.mbfile"
: > "\$MBFILE"
for c in \$(seq 1 22); do
    BF="\${LD_REF}.\${c}"
    if [ -f "\${BF}.bed" ]; then
        echo "\${BF}" >> "\$MBFILE"
    fi
done

# Step 3: GCTA mtCOJO (mirrors m2_mtcojo.smk argv exactly)
OUT_PREFIX="\$OUTDIR/\${TARGET}.mtcojo"
"$GCTA" \\
    --mtcojo-file "\$OUTDIR/cojo_inputs/\${TARGET}.mtcojo.list" \\
    --mbfile "\$MBFILE" \\
    --w-ld-chr "$LDSC_DIR/" \\
    --ref-ld-chr "$LDSC_DIR/" \\
    --out "\$OUT_PREFIX" \\
    > "\$OUT_PREFIX.fire.log" 2>&1

# Step 4: canonicalize output path. Witnessed during M2-POST-M3-08 smoke
# (Task 3): GCTA mtCOJO writes results to <out>.mtcojo.cma (TSV with cols
# SNP A1 A2 freq b se p N bC bC_se bC_pval), where <out> is the value
# passed to --out. Since we pass --out=<target>.mtcojo, the actual output
# is <target>.mtcojo.mtcojo.cma. Try observed + legacy extensions.
if [ ! -f "\$OUT_PREFIX.cojo" ]; then
    for ext in .mtcojo.cma .mtcojo.cma.cojo .cma.cojo .cma _cojo; do
        cand="\${OUT_PREFIX}\${ext}"
        if [ -f "\$cand" ]; then cp "\$cand" "\$OUT_PREFIX.cojo"; break; fi
    done
fi
test -s "\$OUT_PREFIX.cojo"   # MUST be non-empty on success

# Step 5: completion sentinel (used by the harvest runbook)
touch "\$OUTDIR/\${TARGET}.bjob.done"
EOF
        chmod +x "$JOBSCRIPT"

        # Submit
        BSUB_OUT=$(bsub \
            -q long \
            -n 4 \
            -R "rusage[mem=8]" \
            -J "m2p3_08_${STRATUM}_${SHORT}" \
            -o "logs/lsf/m2p3_08_${STRATUM}_${SHORT}.out" \
            -e "logs/lsf/m2p3_08_${STRATUM}_${SHORT}.err" \
            < "$JOBSCRIPT")
        JOB_ID=$(echo "$BSUB_OUT" | grep -oP '(?<=Job <)[0-9]+(?=>)' || echo "UNKNOWN")
        SUBMIT_TS=$(date -Iseconds)
        printf "%s\t%s\t%s\t%s\t%s\t%s\n" \
            "$SUBMIT_TS" "$JOB_ID" "$STRATUM" "$TARGET" "$LD_REF" "$JOBSCRIPT" \
            >> "$BJOBS_TSV"
        echo "[fire_m2_post_m3_08] submitted $STRATUM/$TARGET as job $JOB_ID"
    done
done

cp "$BJOBS_TSV" "$BJOBS_COMMITTED"
echo "[fire_m2_post_m3_08] DONE. Manifest: $BJOBS_TSV (also $BJOBS_COMMITTED)"
