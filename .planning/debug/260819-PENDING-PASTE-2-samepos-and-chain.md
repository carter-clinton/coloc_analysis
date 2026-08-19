# PENDING PASTE #2 — Seth §4/§5 supplement, composed 2026-08-19 ~16:15 EDT, NOT yet pasted

Carter left for home while the 20-region measurement sweep was RUNNING server-side
(Workbench terminal, VM 20260626b; launched ~16:00 EDT; ETA ~1.5-2.5 h; output
lands at /home/jupyter/occ_measure/occ_measure_sample.tsv on completion; harness
cross-check: region 1 MUST reproduce n_occluded == 231 exactly or ALL results are
discarded). This supplement runs ONLY AFTER the sweep finishes. It answers Seth's
two measurement asks: §5 same-position (THE A/B/C discriminator — the old
"same-position = 0" claim is RETIRED as fixture-scope) and §4 chain-vs-span.

Resume order: (1) cat the sweep TSV and paste it to the NCSU session; (2) paste
the block below to the browser agent (or run it directly in the terminal);
(3) paste all outputs back; (4) STOP the app.

--- PASTE FROM HERE ---

SUPPLEMENT (Seth review, 2026-08-19 §4/§5) — run ONLY after the measurement sweep
finishes and its output is pasted. Read-only; aggregate counts only; R6's
occ_measure/ allowance extends to these files.

PART 1 — §5, the same-position measurement (THE decision discriminator; the old
"same-position = 0" claim is RETIRED as fixture-scope, never window-measured).
First Seth's exact one-liners on the persisting region-1 window:
  awk '{print $1":"$4}' data/aou/region1_window.bim | sort | uniq -d | wc -l
  awk '{print $1":"$4}' data/aou/region1_window.bim | sort | uniq -c | sort -rn | head -5
Then the composition sweep over the SAME sampled regions:

cd ~/coloc_analysis && python3 - <<'EOF'
import subprocess, csv
from pathlib import Path
from collections import Counter
OUT = Path("/home/jupyter/occ_measure")
sample = [l.split("\t") for l in open(OUT/"occ_measure_sample.tsv").read().splitlines()[1:]]
man = {r[0]: r for r in csv.reader(open("config/ld_regions.tsv"), delimiter="\t") if len(r) > 6 and r[6] == "AFR"}
print("region_id\tn_rows\tdup_sites\tdup_rows\tmax_mult")
for row in sample:
    rid = row[0]; m = man[rid]
    win = OUT / f"{rid}.sp.bim"
    awk = "($1==\"%s\" || $1==\"chr%s\") && $4>=%s && $4<=%s" % (m[1], m[1], m[14], m[15])
    with open(win, "w") as fh:
        subprocess.run(["awk", awk, "/home/jupyter/afr_cohort.bim"], stdout=fh, check=True)
    pos = Counter((l.split()[0], l.split()[3]) for l in open(win))
    dup = {k: v for k, v in pos.items() if v > 1}
    print(f"{rid}\t{sum(pos.values())}\t{len(dup)}\t{sum(dup.values())}\t{max(dup.values()) if dup else 1}")
    win.unlink()
EOF

PART 2 — §4, the chain-vs-span diagnostic on region 1 (uses the detector's own
edges; ~3 min of compute is normal):

cd ~/coloc_analysis && python3 - <<'EOF'
import sys; sys.path.insert(0, "src/python")
from pathlib import Path
import occlusion_span_filter as osf
rows = osf.load_bim_rows(Path("data/aou/region1_window.bim"))
occluded, edges = osf.detect_occluded_variants(rows)
idx = {r[1]: i for i, r in enumerate(rows)}
occ_i = sorted(idx[v] for v in set(occluded))
who = {v: o for (o, v) in edges}
runs, cur = [], [occ_i[0]]
for a, b in zip(occ_i, occ_i[1:]):
    if b == a + 1: cur.append(b)
    else: runs.append(cur); cur = [b]
runs.append(cur)
multi = [r for r in runs if len(r) >= 2]
print(f"total_occluded={len(occ_i)} runs>=2: {len(multi)}; run-length histogram:",
      {L: sum(1 for r in multi if len(r) == L) for L in sorted({len(r) for r in multi})})
chain = span = 0
for r in multi:
    occluders = {who[rows[i][1]] for i in r}
    if len(occluders) > 1: chain += 1
    else: span += 1
print(f"runs with MULTIPLE distinct occluders (chain): {chain}; single occluder (span): {span}")
EOF

Paste all outputs verbatim. Interpretation happens on the planning side jointly
with Seth — pre-committed: these are measurements, not verdicts; in particular a
nonzero same-position count is NOT automatically a defect (split multiallelics
legitimately share positions) — COMPOSITION decides, not the count alone.

--- PASTE ENDS HERE ---
