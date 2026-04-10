#!/bin/bash
#==============================================================================
# Submit genome-wide coloc jobs in chunks to avoid queue limits
#==============================================================================

GENOME_WIDE_DIR="/share/clintonlab/ckclinto/admixmap/genome_wide"
cd "$GENOME_WIDE_DIR"

# Get arguments or use defaults
START=${1:-1}
END=${2:-1000}
CHUNK_SIZE=1000

N_TOTAL=$(wc -l < config/coloc_pair_ids.txt)

if [[ $END -gt $N_TOTAL ]]; then
  END=$N_TOTAL
fi

echo "Submitting jobs $START to $END (of $N_TOTAL total)"

# Create temporary submission script for this chunk
cat > scripts/submit_chunk_${START}_${END}.sh << EOF
#!/bin/bash
#BSUB -J gw_coloc[${START}-${END}]
#BSUB -o logs/coloc_%I.out
#BSUB -e logs/coloc_%I.err
#BSUB -n 1
#BSUB -R "rusage[mem=4GB]"
#BSUB -W 0:30
#BSUB -q short

cd $GENOME_WIDE_DIR
source ~/.bashrc
export PATH="/share/clintonlab/ckclinto/admixmap/genome_wide/bin/bin:\$PATH"
conda activate /gpfs_common/share01/clintonlab/ckclinto/admix_map/.conda/admix_map_r_hyprcoloc 2>/dev/null || true

PAIR_ID=\$(sed -n "\${LSB_JOBINDEX}p" config/coloc_pair_ids.txt)
if [[ -z "\$PAIR_ID" ]]; then
  echo "No pair ID for index \$LSB_JOBINDEX"
  exit 0
fi

OUTPUT_FILE="results/coloc/\${PAIR_ID}.json"
if [[ -f "\$OUTPUT_FILE" ]]; then
  echo "Output exists, skipping"
  exit 0
fi

echo "Processing: \$PAIR_ID"
Rscript scripts/run_coloc_genomewide.R \
  --manifest config/genomewide_coloc_manifest.tsv \
  --pair-id "\$PAIR_ID" \
  --output "\$OUTPUT_FILE"
EOF

bsub < scripts/submit_chunk_${START}_${END}.sh

echo "Submitted chunk $START-$END"
