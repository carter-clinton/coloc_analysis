#!/bin/bash
# Lift a harmonized sumstats file GRCh38 -> GRCh37 with the liftover_asthma_afr.sh method
# (UCSC liftOver, hg38ToHg19 chain, 1-bp BED keyed by line number, default minMatch),
# writing a NEW file; the input is never modified. Rows lifted onto a minus-strand chain block get
# REF/ALT complemented (SNVs; A/T and C/G listed in WORKDIR/minus_strand_palindromic.tsv) or dropped
# (non-SNV: the anchor base and span cannot be rebuilt without a GRCh37 FASTA).
#   usage: liftover_sumstats_hg38_to_hg19.sh IN.tsv.bgz OUT.tsv.bgz LIFTOVER_BIN CHAIN WORKDIR
# Dropped rows (unmapped, non-canonical contig, chromosome change, minus-strand non-SNV) are logged in WORKDIR.
set -euo pipefail

IN=$1; OUT=$2; LIFTOVER=$3; CHAIN=$4; WORK=$5
ENV_BIN=/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin
mkdir -p "$WORK"
[[ -e "$OUT" ]] && { echo "refusing to overwrite $OUT" >&2; exit 1; }

# CHR 23 is X in the harmonized files; liftOver needs the UCSC name.
zcat "$IN" | awk -F'\t' -v OFS='\t' '
  NR==1 { for (i=1;i<=NF;i++) { if ($i=="CHR") c=i; if ($i=="POS") p=i }; next }
  { chr=$c; if (chr=="23") chr="X"; if (chr !~ /^chr/) chr="chr" chr; print chr, $p-1, $p, NR, 0, "+" }
' > "$WORK/input.bed"

"$LIFTOVER" "$WORK/input.bed" "$CHAIN" "$WORK/lifted.bed" "$WORK/unmapped.bed"

python3 - "$IN" "$WORK" <<'PY'
import gzip, json, re, sys
src, work = sys.argv[1], sys.argv[2]
canon = {str(i) for i in range(1, 23)} | {"X", "Y"}
n = {"input": 0, "lifted": 0, "unmapped": 0, "dropped_noncanonical": 0, "dropped_chr_change": 0,
     "dropped_minus_strand_non_snv": 0, "kept": 0, "kept_minus_strand_complemented": 0,
     "kept_minus_strand_palindromic": 0}
COMP = str.maketrans("ACGTacgt", "TGCAtgca")
PAL = {("A", "T"), ("T", "A"), ("C", "G"), ("G", "C")}
def norm(c):
    c = re.sub(r"^chr", "", c)
    return "X" if c == "23" else c
lifted = open(f"{work}/lifted.bed")
drop = open(f"{work}/dropped_rows.tsv", "w")
drop.write("line\treason\tCHR\tPOS\tSNP_ID\tlifted_chr\tlifted_pos\n")
nxt = lifted.readline().split("\t")
with gzip.open(src, "rt") as fin, open(f"{work}/lifted_unsorted.tsv", "w") as fout:
    hdr = fin.readline().rstrip("\n").split("\t")
    ci, pi, si = hdr.index("CHR"), hdr.index("POS"), hdr.index("SNP_ID")
    ri, ai = hdr.index("REF"), hdr.index("ALT")
    pal = open(f"{work}/minus_strand_palindromic.tsv", "w")
    pal.write("line\tCHR\tPOS_GRCh37\tSNP_ID\tREF_GRCh38\tALT_GRCh38\n")
    open(f"{work}/header.tsv", "w").write("\t".join(hdr) + "\n")
    last = 0
    for ln, line in enumerate(fin, start=2):
        n["input"] += 1
        f = line.rstrip("\n").split("\t")
        if len(nxt) == 6 and int(nxt[3]) == ln:
            assert int(nxt[3]) > last
            last = int(nxt[3])
            n["lifted"] += 1
            lc, lp, strand = norm(nxt[0]), nxt[2], nxt[5].rstrip("\n")
            nxt = lifted.readline().split("\t")
            if lc not in canon:
                n["dropped_noncanonical"] += 1
                drop.write(f"{ln}\tnoncanonical\t{f[ci]}\t{f[pi]}\t{f[si]}\t{lc}\t{lp}\n")
                continue
            if lc != norm(f[ci]):
                n["dropped_chr_change"] += 1
                drop.write(f"{ln}\tchr_change\t{f[ci]}\t{f[pi]}\t{f[si]}\t{lc}\t{lp}\n")
                continue
            if strand == "-":
                r, a = f[ri].upper(), f[ai].upper()
                if not (len(r) == 1 and len(a) == 1 and r in "ACGT" and a in "ACGT"):
                    n["dropped_minus_strand_non_snv"] += 1
                    drop.write(f"{ln}\tminus_strand_non_snv\t{f[ci]}\t{f[pi]}\t{f[si]}\t{lc}\t{lp}\n")
                    continue
                if (r, a) in PAL:
                    n["kept_minus_strand_palindromic"] += 1
                    pal.write(f"{ln}\t{f[ci]}\t{lp}\t{f[si]}\t{f[ri]}\t{f[ai]}\n")
                f[ri], f[ai] = f[ri].translate(COMP), f[ai].translate(COMP)
                n["kept_minus_strand_complemented"] += 1
            else:
                assert strand == "+", strand
            f[pi] = lp
            fout.write("\t".join(f) + "\n")
            n["kept"] += 1
        else:
            n["unmapped"] += 1
            drop.write(f"{ln}\tunmapped\t{f[ci]}\t{f[pi]}\t{f[si]}\t\t\n")
    assert nxt == [""], "lifted.bed not consumed in input order"
assert n["input"] == n["lifted"] + n["unmapped"]
assert n["lifted"] == n["kept"] + n["dropped_noncanonical"] + n["dropped_chr_change"] + n["dropped_minus_strand_non_snv"]
json.dump(n, open(f"{work}/counts.json", "w"), indent=1)
print(json.dumps(n))
PY

export LC_ALL=C
{ cat "$WORK/header.tsv"; sort -T "$WORK" -S 8G -k1,1V -k2,2n "$WORK/lifted_unsorted.tsv"; } | "$ENV_BIN/bgzip" -c > "$OUT"
"$ENV_BIN/tabix" -s1 -b2 -e2 -S1 "$OUT"
# Rows sharing CHR:POS:REF:ALT after the lift (several GRCh38 sites onto one GRCh37 site).
zcat "$OUT" | awk -F'\t' 'NR>1{print $1":"$2":"$3":"$4}' | sort -T "$WORK" -S 4G | uniq -d > "$WORK/duplicate_keys.txt"
echo "duplicate_keys $(wc -l < "$WORK/duplicate_keys.txt")"
sha256sum "$OUT" | tee "$WORK/sha256.txt"
