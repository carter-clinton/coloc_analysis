#!/usr/bin/env bash
# Route L (D-12b): extract PATH (default run_susie_rss.R) and every repo file it source()s at REF into
# data/r4/legacy_code/<REF>/<path>, plus data/r4/legacy_code/<stem>_<REF>.R for each .R PATH.
# Rewrites the rows for those files in $MAN/legacy_code_sha256.tsv (ref, rel_path, sha256).
#   bash bin/r4_extract_legacy_code.sh <REF> [PATH...]
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
REF=${1:?usage: bash bin/r4_extract_legacy_code.sh <REF> [PATH...]}
shift
TOP=("$@")
[ ${#TOP[@]} -gt 0 ] || TOP=(src/legacy/region_analysis/scripts/run_susie_rss.R)
MANIFEST=.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/legacy_code_sha256.tsv
OUT=data/r4/legacy_code

git rev-parse --verify --quiet "$REF^{commit}" >/dev/null || { echo "unknown ref $REF" >&2; exit 2; }
if git fsck --connectivity-only 2>&1 | grep -E "^(missing|broken)" ; then
    echo "REFUSED: git fsck reports missing/broken objects" >&2
    exit 3
fi

# Repo files source()d by the script at REF (literal paths; resolved against the repo root and the
# script's own directory). A non-literal source() is refused rather than guessed.
deps() {
    git show "$REF:$1" | { grep -oE '(^|[^A-Za-z_.])(sys\.)?source\([^)]*\)' || true; } | sed -E 's/^[^s]*//' | while read -r call; do
        lit=$(printf '%s' "$call" | sed -nE 's/.*source\(\s*["'"'"']([^"'"'"']+)["'"'"'].*/\1/p')
        [ -n "$lit" ] || { echo "REFUSED: non-literal $call in $1@$REF" >&2; exit 4; }
        for cand in "$lit" "$(dirname "$1")/$lit"; do
            if git cat-file -e "$REF:$cand" 2>/dev/null; then echo "$cand"; continue 2; fi
        done
        echo "REFUSED: $lit (sourced by $1) not in $REF" >&2; exit 4
    done
}

for t in "${TOP[@]}"; do git cat-file -e "$REF:$t" 2>/dev/null || { echo "$t not in $REF" >&2; exit 2; }; done
FILES=("${TOP[@]}")
i=0
while [ $i -lt ${#FILES[@]} ]; do
    found=$(deps "${FILES[$i]}")
    while read -r d; do
        [ -n "$d" ] || continue
        printf '%s\n' "${FILES[@]}" | grep -qxF "$d" || FILES+=("$d")
    done <<< "$found"
    i=$((i + 1))
done

mkdir -p "$OUT/$REF"
TMP=$(mktemp -p "$OUT")
for f in "${FILES[@]}"; do
    mkdir -p "$OUT/$REF/$(dirname "$f")"
    chmod u+w "$OUT/$REF/$f" 2>/dev/null || true
    git show "$REF:$f" > "$OUT/$REF/$f"
    chmod a-w "$OUT/$REF/$f"
    printf '%s\t%s\t%s\n' "$REF" "$OUT/$REF/$f" "$(sha256sum "$OUT/$REF/$f" | cut -d' ' -f1)" >> "$TMP"
done
for t in "${TOP[@]}"; do
    case "$t" in *.R) ;; *) continue ;; esac
    CONV="$OUT/$(basename "$t" .R)_$REF.R"
    chmod u+w "$CONV" 2>/dev/null || true
    cp "$OUT/$REF/$t" "$CONV"
    chmod a-w "$CONV"
    printf '%s\t%s\t%s\n' "$REF" "$CONV" "$(sha256sum "$CONV" | cut -d' ' -f1)" >> "$TMP"
done

[ -s "$MANIFEST" ] || printf 'ref\trel_path\tsha256\n' > "$MANIFEST"
{ head -1 "$MANIFEST"; tail -n +2 "$MANIFEST" | awk -F'\t' 'NR == FNR { new[$2] = 1; next } !($2 in new)' "$TMP" -; cat "$TMP"; } > "$MANIFEST.new"
mv "$MANIFEST.new" "$MANIFEST"
rm -f "$TMP"
echo "extracted ${#FILES[@]} file(s) at $REF:"
printf '  %s\n' "${FILES[@]}"
