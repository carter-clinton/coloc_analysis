# PENDING PASTE #3 — site-basis occlusion sweep (per Seth C2/C3), for the next VM session

Purpose: re-measure the 21-region occlusion distribution on SITE basis (occluded
SITES / total SITES per region) so the recalibrated clause-(d) gate — ceiling =
3x measured median, purpose-anchored per Seth's C3 derivation — instantiates its
number once, on the representation-invariant quantity. Runs the ACTUAL position
grouping (not Seth's approximate run-collapse). Expected ~2-2.5 h; VM must be
STARTED first (Carter UI) and STOPPED after.

--- PASTE FROM HERE ---

RULED SITE-BASIS SWEEP (read-only; no LD, no banking; same pre-committed 21-region
sample as the row-basis sweep; R6's occ_measure/ allowance applies). Harness
cross-check: region 1 must reproduce n_occluded_rows == 231 EXACTLY or all
results are discarded.

cd ~/coloc_analysis && python3 - <<'EOF'
import subprocess, csv, statistics
from pathlib import Path
OUT = Path("/home/jupyter/occ_measure")
import sys; sys.path.insert(0, "src/python")
import occlusion_span_filter as osf
sample = [l.split("\t")[0] for l in open(OUT/"occ_measure_sample.tsv").read().splitlines()[1:]]
man = {r[0]: r for r in csv.reader(open("config/ld_regions.tsv"), delimiter="\t") if len(r) > 6 and r[6] == "AFR"}
print("region_id\tn_rows\tn_sites\tocc_rows\tocc_sites\trow_frac_pct\tsite_frac_pct\tinflation")
site_fracs = []
results = []
for rid in sample:
    m = man[rid]
    win = OUT / f"{rid}.sb.bim"
    awk = "($1==\"%s\" || $1==\"chr%s\") && $4>=%s && $4<=%s" % (m[1], m[1], m[14], m[15])
    with open(win, "w") as fh:
        subprocess.run(["awk", awk, "/home/jupyter/afr_cohort.bim"], stdout=fh, check=True)
    rows = osf.load_bim_rows(win)
    occluded, _edges = osf.detect_occluded_variants(rows)
    occset = set(occluded)
    n_rows = len(rows)
    all_sites = {(r[0], r[3]) for r in rows}
    occ_rows = [r for r in rows if r[1] in occset]
    occ_sites = {(r[0], r[3]) for r in occ_rows}
    rf = 100.0 * len(occ_rows) / n_rows
    sf = 100.0 * len(occ_sites) / len(all_sites)
    infl = (len(occ_rows) / len(occ_sites)) if occ_sites else 0.0
    site_fracs.append(sf)
    results.append((rid, n_rows, len(all_sites), len(occ_rows), len(occ_sites), rf, sf, infl))
    print(f"{rid}\t{n_rows}\t{len(all_sites)}\t{len(occ_rows)}\t{len(occ_sites)}\t{rf:.4f}\t{sf:.4f}\t{infl:.2f}", flush=True)
    win.unlink()
    if rid == "m2_region_00001":
        assert len(occ_rows) == 231, f"HARNESS CROSS-CHECK FAILED: region 1 gave {len(occ_rows)} occluded rows, expected 231 — STOP"

with open(OUT / "occ_measure_sitebasis.tsv", "w") as fh:
    fh.write("region_id\tn_rows\tn_sites\tocc_rows\tocc_sites\trow_frac_pct\tsite_frac_pct\trow_site_inflation\n")
    for t in results:
        fh.write("\t".join(str(x) for x in t) + "\n")

sf_sorted = sorted(site_fracs)
med = statistics.median(sf_sorted)
mad = statistics.median([abs(x - med) for x in sf_sorted])
print(f"\nSITE-BASIS SUMMARY n={len(sf_sorted)}: min={sf_sorted[0]:.4f}% median={med:.4f}% "
      f"max={sf_sorted[-1]:.4f}%; robust_sigma(1.4826*MAD)={1.4826*mad:.4f}%")
print(f"CANDIDATE CEILING (Seth C3, 3x site-basis median): {3*med:.4f}%")
print(f"margin over observed site-basis max: {3*med/sf_sorted[-1]:.2f}x")
mean_infl = statistics.mean(t[7] for t in results)
print(f"mean row/site inflation across sample: {mean_infl:.2f}x (Seth's run-collapse estimate was ~1.42x for region 1)")
EOF

Paste the FULL stdout verbatim plus:
  wc -l /home/jupyter/occ_measure/occ_measure_sitebasis.tsv
Aggregate counts only — egress-safe. On any exception or harness failure: STOP,
paste verbatim, wait. When results are pasted, Carter STOPS the app.

--- PASTE ENDS HERE ---
