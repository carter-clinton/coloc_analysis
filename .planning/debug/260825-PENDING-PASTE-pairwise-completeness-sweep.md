# PENDING PASTE — pairwise-completeness sweep (21-region), for the next VM session

Purpose: MEASURE what the Stage B halt left open. `m2_region_00057` carries a
confined pairwise NaN between the 1 bp deletion `chr15:20394741:AT:A` and the SNP
`chr15:20394743:T:C`, one base past the pre-registered REF span. The mechanism is
CONFIRMED (0 of 871 deletion carriers called at the partner → the deletion is
invariant within the 71048-sample intersection → plink writes `0/0` → NaN), but the
PREVALENCE, the true BOUNDARY WIDTH (and whether it is one-sided) and whether a
PARTIAL-confounding tail exists are all UNKNOWN and **cannot be inferred from n=1**.
Provenance: `.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md`.

This sweep is a **pure genotype property** — no `--r`, no LD recompute, no 42 GB
matrices. It reads only the candidate variants' `.bed` blocks (a ~6,000-candidate
region is roughly 110 MB of seeks against a ~354 GB file). Expect minutes per
region, not hours. Read-only; nothing is banked, nothing is excluded, no criterion
moves. **This sweep calls no plink at all.**

Status: **WRITTEN AND NOT RUN.** As of the NCSU session that authored it, the
instrument is built and tested at $0 and has never touched data. The VM is stopped.
An agent never fires anything billable — Carter starts the VM and gives the go.

--- PASTE FROM HERE ---

PAIRWISE-COMPLETENESS SWEEP (read-only; no LD, no plink, no banking; the SAME
pre-committed 21-region sample as the row-basis and site-basis sweeps; R6's
occ_measure/ allowance applies). Run the STEPS IN ORDER. Do not skip STEP 1.
On ANY exception: STOP, paste the output verbatim, change nothing, wait.

=== STEP 0 — FRESHNESS. Prove which code is about to run. ===

cd ~/coloc_analysis
git fetch
git checkout m3-W2-aou-deltas
git pull --ff-only
git log -1 --oneline
ls -l src/python/pairwise_completeness_scan.py

Paste the SHA and the ls line back BEFORE running anything else.

⚠ NCSU must have been PUSHED first. The NCSU tree routinely runs many commits
ahead of origin; if it was not pushed, this clone silently runs STALE code and
every number below is attributable to the wrong commit. If `git log -1` does not
show a `quick-260825-ngh` commit touching pairwise_completeness_scan.py, or if
`ls -l` reports no such file: STOP and say so. Do not proceed.

=== STEP 1 — THE HARNESS CROSS-CHECK, ALONE, BEFORE THE SWEEP. ===

Run the scanner on m2_region_00057 ONLY and confirm it reproduces the pair we
already measured by hand. Run this even though 00057 is inside the 21-region
sample: a harness that cannot reproduce a known answer cannot be trusted to
produce unknown ones.

mkdir -p /home/jupyter/occ_measure
python3 src/python/pairwise_completeness_scan.py \
  --bfile-prefix /home/jupyter/afr_cohort \
  --region-id m2_region_00057 \
  --chr 15 \
  --from-bp 20394600 \
  --to-bp 20394900 \
  --window-bp 25 \
  --out /home/jupyter/occ_measure/pcs_00057_crosscheck.tsv \
  --summary /home/jupyter/occ_measure/pcs_00057_crosscheck.json

Then print ONLY the cross-checked row:

python3 - <<'EOF'
import csv
P = "/home/jupyter/occ_measure/pcs_00057_crosscheck.tsv"
DEL, PARTNER = "chr15:20394741:AT:A", "chr15:20394743:T:C"
rows = [r for r in csv.DictReader(open(P), delimiter="\t")
        if {r["del_vid"], r["partner_vid"]} == {DEL, PARTNER}]
print("matching rows:", len(rows))
for r in rows:
    print({k: r[k] for k in ("del_vid", "partner_vid", "offset", "already_occluded",
                             "undefined", "invariant_member", "n_both_called",
                             "del_carriers_marginal", "del_carriers_lost",
                             "del_carriers_lost_frac", "del_maf_marginal",
                             "confounding_pattern")})
assert len(rows) == 1, "CROSS-CHECK FAILED: expected exactly 1 row for the known pair"
r = rows[0]
EXPECT = {"offset": "1", "undefined": "True", "n_both_called": "71048",
          "del_carriers_lost": "871", "already_occluded": "False",
          "invariant_member": "deletion"}
bad = {k: (r[k], v) for k, v in EXPECT.items() if r[k] != v}
assert not bad, f"CROSS-CHECK FAILED (got, expected): {bad}"
print("CROSS-CHECK PASSED: 20394741 x 20394743 -> offset +1, undefined, "
      "n_both_called 71048, del_carriers_lost 871")
EOF

⛔ ON ANY MISMATCH OR ASSERTION FAILURE: **STOP. Paste the output verbatim.
DISCARD ALL RESULTS. Do NOT run STEP 2. Do NOT adjust the expected numbers, the
window, or the code to make it pass.** A harness that disagrees with the one pair
we measured by hand is broken, and every number it would produce is worthless.
(This mirrors the region-1 `231` cross-check that guarded the site-basis sweep.)

=== STEP 2 — THE SWEEP over the pre-committed 21-region sample. ===

Only after STEP 1 prints CROSS-CHECK PASSED.

python3 - <<'EOF'
import subprocess, sys
SAMPLE = "/home/jupyter/occ_measure/occ_measure_sample.tsv"
ids = [l.split("\t")[0] for l in open(SAMPLE).read().splitlines()[1:] if l.strip()]
print("regions in the pre-committed sample:", len(ids))
cmd = [sys.executable, "src/python/pairwise_completeness_scan.py",
       "--bfile-prefix", "/home/jupyter/afr_cohort",
       "--regions-tsv", "config/ld_regions.tsv",
       "--region-ids", ",".join(ids),
       "--window-bp", "25",
       "--out", "/home/jupyter/occ_measure/pcs_pairs.tsv",
       "--summary", "/home/jupyter/occ_measure/pcs_summary.json"]
print(" ".join(cmd), flush=True)
raise SystemExit(subprocess.call(cmd))
EOF

wc -l /home/jupyter/occ_measure/pcs_pairs.tsv

PASTE BACK: the FULL stdout of the sweep (the per-region summary table, the pooled
offset histogram, the pooled lost-frac bins) plus that `wc -l` line, plus the
contents of /home/jupyter/occ_measure/pcs_summary.json.

=== EGRESS RULE ===

AGGREGATE COUNTS, FRACTIONS and VARIANT COORDINATES/IDS ONLY may cross back.
NEVER per-sample data of any kind. The full per-pair TSV
(/home/jupyter/occ_measure/pcs_pairs.tsv) STAYS IN-PERIMETER — do not paste it,
do not copy it out. The summary JSON and the stdout table are the deliverables.

=== OPERATIONAL NOTES ===

* The VM must be STARTED by Carter and STOPPED by Carter after. An agent NEVER
  fires anything billable without Carter's explicit go.
* `export PATH="$HOME/bin:$PATH"` is PER-SHELL and must be re-issued in each new
  terminal. Listed here only because this shell is shared with the fire runbooks:
  **this sweep calls no plink at all**, so that export is NOT on its critical path.
* Check `df -h /home/jupyter` before writing. The Stage B leftovers
  (`m2_region_00057.ld.bin` is the FORENSIC ARTIFACT — do not delete it) were not
  re-measured after Stage B.
* On ANY exception: STOP and paste verbatim. No retry, no edit, no improvisation.

=== WHAT THIS DOES NOT DECIDE ===

This produces MEASUREMENTS ONLY. It changes no criterion, no threshold, no span
rule and no NaN policy, and it does not widen the pre-registered occlusion span by
one base or any other amount. It reports counts and distributions; it reports no
rate and no prevalence, because 21 regions of 276 do not determine one and because
the exclusion criterion is what is pre-registered at osf.io/trsx5.

Adjudication — whether the criterion is extended, whether an explicit
pairwise-completeness policy is added, and what Stage C's error-handling posture
becomes — is a SEPARATE, pre-registration question that happens AFTER the numbers
exist, brief-blind, with Seth. Do not let a number from this sweep become a rule in
the same conversation that produced it. That is exactly how the withdrawn `0.0005`
constant was born.

--- PASTE ENDS HERE ---

## What to look for when the results come back (NOT predictions)

The three OPEN questions and the field that speaks to each. **No expected value is
stated for any of them, deliberately** — see the sweep design in the halt record §
"PREVALENCE SWEEP".

| OPEN question | The field that measures it |
|---|---|
| (a) prevalence of undefined pairs | `n_undefined_distinct_pairs`, split into `n_undefined_already_occluded` (the posted rule already covers these) vs `n_undefined_not_already_occluded` (the NEWLY DISCOVERED class) |
| (b) the true boundary width, and whether it is one-sided | `undefined_offset_histogram` — the empirical offset distribution over the undefined set, swept on BOTH sides. NEGATIVE offsets are upstream of `pos`; a nonempty negative side would mean the posted one-sided rule under-covers in a second direction. |
| (c) whether a partial-confounding tail exists | `defined_carriers_lost_frac_bins` and `n_defined_lost_frac_ge_0p9` over DEFINED rows — finite-`r` pairs computed on carrier-depleted subsamples, which no NaN check anywhere in the pipeline can see |

Region 1 is the negative control already in hand: 102,421 in-window rows, 7,951
multi-base-REF rows, 38,595,391,746 bytes re-read, ZERO NaN. That establishes only
that region 1 held no *perfectly* confounded pair — **not** that it is free of
deletion-linked missingness bias. Column (c) is the first instrument able to tell
those two apart.
