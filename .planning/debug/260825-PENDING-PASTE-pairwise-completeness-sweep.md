# PENDING PASTE — pairwise-completeness sweep (21-region), for the next VM session

Purpose: MEASURE what the Stage B halt left open. `m2_region_00057` carries a
confined pairwise NaN between the 1 bp deletion `chr15:20394741:AT:A` and the SNP
`chr15:20394743:T:C`, one base past the pre-registered REF span. The mechanism is
CONFIRMED (0 of 871 deletion carriers called at the partner → the deletion is
invariant within the 71048-sample intersection → plink writes `0/0` → NaN), but the
PREVALENCE, the true BOUNDARY WIDTH (and whether it is one-sided) and whether a
PARTIAL-confounding tail exists are all UNKNOWN and **cannot be inferred from n=1**.
Provenance: `.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md`.

The sweep itself (STEPS 2-3) is a **pure genotype property** — no `--r`, no LD
recompute, no 42 GB matrices. It reads only the candidate variants' `.bed` blocks
(a ~6,000-candidate region is roughly 110 MB of seeks against a ~354 GB file).
Expect minutes per region, not hours. Read-only; nothing is banked, nothing is
excluded, no criterion moves.

**STEP 1 is different, and it comes first.** The whole scanner rests on ONE
unverified assumption: that plink1.9 `--r` correlates over PAIRWISE-COMPLETE
observations. STEP 1 calls plink1.9 **three times on 2-3 variants** to test that
assumption against the real cohort before any number is generated. STEPS 2-3 call
no plink. Total plink cost: seconds.

Status: **WRITTEN AND NOT RUN — including the STEP 1 falsifier.** As of the NCSU
session that authored it, the instrument is built, adversarially reviewed,
remediated and tested at $0, and has never touched data. The falsifier is written
and unrun, so **the pairwise-complete premise is UNCONFIRMED.** The VM is stopped.
An agent never fires anything billable — Carter starts the VM and gives the go.

--- PASTE FROM HERE ---

PAIRWISE-COMPLETENESS SWEEP + PLINK PAIRWISE-COMPLETE FALSIFIER (read-only; no LD
recompute, no banking; the SAME pre-committed 21-region sample as the row-basis and
site-basis sweeps; R6's occ_measure/ allowance applies, and it covers the
falsifier's small plink working files written inside /home/jupyter/occ_measure/).
Run the STEPS IN ORDER. Do not skip STEP 1.
On ANY exception: STOP, paste the output verbatim, change nothing, wait.

=== STEP 0 — FRESHNESS + ENVIRONMENT. Prove which code, and which plink, is about to run. ===

REQUIRED FIRST ACTION in EVERY new shell (it is PER-SHELL and does not survive a
new tab, a kernel restart or a VM stop/start):

export PATH="$HOME/bin:$PATH"

Then:

cd ~/coloc_analysis
git fetch
git checkout m3-W2-aou-deltas
git pull --ff-only
git log -1 --oneline
ls -l src/python/pairwise_completeness_scan.py

Paste the SHA and the ls line back BEFORE running anything else.

⚠ NCSU must have been PUSHED first. The NCSU tree routinely runs many commits
ahead of origin; if it was not pushed, this clone silently runs STALE code and
every number below is attributable to the wrong commit.

--- the BEHAVIOURAL FRESHNESS GATE. Pin what the code DOES, not what a commit is called. ---

WHY THIS IS NOT A COMMIT-NAME CHECK. Until 2026-08-28 this gate said "STOP unless
`git log -1` shows a `quick-260825-qpf` commit". That gate was a SPOOF in both
directions, MEASURED:

* The CONTAMINATED 2026-08-26 run pulled to `769afa6`, whose SUBJECT LINE contains
  the string `quick-260825-qpf`
  (`git log -1 --format='%s' 769afa6 | grep -c 'quick-260825-qpf'` -> **1**). So the
  old gate PASSED on the 8x-duplication code and every count that run produced is
  void.
* It also FALSE-STOPPED on `352ac9e`
  (`git log -1 --format='%s' 352ac9e | grep -c 'quick-260825-qpf'` -> **0**), a
  perfectly good checkout.

A commit SUBJECT is prose. Gate on the CONTENT of the file that will run, and on
what that file can DO. Run all four checks below; each has an EXPECT and a STOP.

(i) git status --porcelain src/python/pairwise_completeness_scan.py

EXPECT: NO OUTPUT AT ALL. Any output means the working tree has a local edit, so
the hash in (ii) is not the code that will run. STOP.

(ii) md5sum src/python/pairwise_completeness_scan.py
     stat -c '%s' src/python/pairwise_completeness_scan.py

EXPECT exactly:

  e03078ff73502c3c877b0d2ebf93941d
  73772

Any other hash or size means this clone is NOT running the reviewed instrument.
STOP. (Do not "update" these values from what the VM reports — that inverts the
gate. See HOW TO REGENERATE below.)

(iii) git log -1 --format='%h %s' -- src/python/pairwise_completeness_scan.py

EXPECT the short hash `cb199b6` (the quick-260828-uej T1 commit: write the TSV
BEFORE the reconciliation, quarantine to `.SUSPECT` on disagreement). A different
commit means the file moved after this gate was written — STOP and regenerate.

(iv) THE CAPABILITY CHECK. A POSITIVE test that the code can do the one thing
every number below depends on: read `config/ld_regions.tsv` on its REAL key.

python3 - <<'EOF'
import sys
sys.path.insert(0, "src/python")
import pairwise_completeness_scan as pcs
windows = pcs._read_regions_tsv("config/ld_regions.tsv", None)
ids = {w[0] for w in windows}
print("manifest windows:", len(windows), "distinct region ids:", len(ids))
assert len(windows) == 276, "EXPECTED 276 windows, got %d" % len(windows)
assert len(ids) == 276, "EXPECTED 276 distinct region ids, got %d" % len(ids)
print("CAPABILITY CHECK PASSED")
EOF

EXPECT exactly these two lines:

  manifest windows: 276 distinct region ids: 276
  CAPABILITY CHECK PASSED

WHAT EACH FAILURE MEANS:

* `552` windows against `276` ids = THE ANCESTRY-BLIND READ. The manifest is keyed
  on (region_id x ancestry) — 553 lines = 1 header + 276 ids x 2 — and this code
  is returning every window TWICE. That is the 8x-duplication defect that voided
  the 2026-08-26 sweep. MEASURED: a pre-fix checkout returns exactly `552` / `276`
  through this same call. **STOP.**
* `TypeError: _read_regions_tsv() got an unexpected keyword argument` = a pre-fix
  checkout reached through the keyword call form (MEASURED at `d8f4d54^`). **STOP.**
* Anything else, including any traceback: **STOP.** Paste it verbatim, change
  nothing.

⚠ DO NOT "FIX" THIS BLOCK BY ADDING A TWO-DASH ANCESTRY COMMAND-LINE FLAG
ANYWHERE IN THIS DOCUMENT. The STEP 3 sweep command is correct ONLY because
`DEFAULT_ANCESTRY == "AFR"` in the scanner, and
`tests/m3/test_pairwise_completeness_scan.py::test_pending_paste_step3_carries_no_ancestry_flag_so_the_default_is_load_bearing`
asserts that this file contains that token ZERO times. That is why the check above
is expressed in Python against `_read_regions_tsv` rather than as a flag.

HOW TO REGENERATE THIS GATE (the only legitimate way to change (i)-(iii); run at
NCSU, on a clean tree, AFTER the scanner legitimately changes, then update the
three values above and re-run the test suite so the enforcers agree):

  git status --porcelain src/python/pairwise_completeness_scan.py
  md5sum src/python/pairwise_completeness_scan.py
  stat -c '%s' src/python/pairwise_completeness_scan.py
  git log -1 --format='%h %s' -- src/python/pairwise_completeness_scan.py

--- the PINNED plink1.9 build ---

which plink1.9
plink1.9 --version

EXPECT exactly: PLINK v1.90b7.2 64-bit (11 Dec 2023)

Any other version is a STOP. In particular a PLINK 2.x binary shimmed as
`plink1.9` is a STOP: PLINK 2.x `--r square bin4` semantics differ, which is
precisely the thing STEP 1 is measuring. Do NOT verify with a
`which plink || which plink1.9` style check — that form passed on the WRONG binary
twice; run `plink1.9 --version` and read the version line.

If `plink1.9` is absent, the pinned install is ONE command:

  mkdir -p ~/bin && cd ~/bin && wget -q https://s3.amazonaws.com/plink1-assets/plink_linux_x86_64_20231211.zip && unzip -o plink_linux_x86_64_20231211.zip plink && mv -f plink plink1.9 && chmod +x plink1.9 && cd ~/coloc_analysis

A browser agent's safety layer will REFUSE to run that download-and-execute line,
and it is CORRECT to refuse. CARTER pastes that one command into the same tab
himself, then re-runs `plink1.9 --version`. Do not work around the refusal, and
never substitute the VM image's own `plink` (it is v1.9.0-b.8, not the pin).

--- the .fam FOUNDER COUNT (a FIELD RECORD, not a decision) ---

wc -l < /home/jupyter/afr_cohort.fam
awk '$3=="0" && $4=="0"' /home/jupyter/afr_cohort.fam | wc -l

plink1.9's LD calculations consider FOUNDERS ONLY by default, and the production
square command passes `--nonfounders` to count all samples. These two numbers
RECORD whether that distinction is even live in this cohort instead of assuming
it: if they are equal, every sample is a founder and the flag is a no-op here. Do
NOT state an expected value — report whatever they say, and change nothing on the
strength of them.

--- the .bim the banked pair_keys are RELATIVE TO (a FIELD RECORD) ---

wc -l /home/jupyter/afr_cohort.bim

EXPECT 20767864. A DIFFERENT NUMBER IS A STOP. `pair_key` is a GLOBAL `.bim` row
index, not a coordinate: the 13 banked pair_keys from the contaminated sweep, and
every pair_key this sweep emits, are comparable ONLY against a byte-identical
`.bim`. A rebuilt or re-filtered cohort silently renumbers every one of them, and
nothing downstream would notice.

ls -l --time-style=full-iso /home/jupyter/afr_cohort.bed /home/jupyter/afr_cohort.bim /home/jupyter/afr_cohort.fam

--- the interpreter that will run the scan (FIELD RECORDS) ---

python3 -V
python3 -c "import numpy; print('numpy', numpy.__version__)"

These blocks are RECORDS, in the same class as the founder counts above: they are
pasted back so the numbers can be attributed later. Only the `.bim` line count
carries a STOP.

--- disk ---

df -h /home/jupyter

The Stage B leftovers (`m2_region_00057.ld.bin` is the FORENSIC ARTIFACT — do not
delete it) were not re-measured after Stage B.

=== STEP 1 — THE plink PAIRWISE-COMPLETE FALSIFIER. Test the premise BEFORE producing any number. ===

THE STAKES, stated plainly. The scanner assumes plink1.9 `--r` computes the
correlation over PAIRWISE-COMPLETE observations — the samples non-missing at BOTH
variants of the pair. The evidence for that today is CIRCUMSTANTIAL: in
`m2_region_00057` both marginals were variable, both diagonals were 1.0, and
exactly one symmetric NaN pair appeared. That is consistent with pairwise-complete,
but it is not a proof of the implementation contract. If plink instead
MEAN-IMPUTES the missing genotypes, or drops any sample missing at ANY variant in
the window (LISTWISE deletion over the window), then the scanner measures the
wrong thing and **every number the sweep would produce is VOID**.

This step is read-only, costs three tiny plink runs on 2-3 variants, and decides
it. It creates no individual-level file: it deliberately does NOT use `--recode A`,
which would materialise a 73,122-row dosage table in-perimeter.

--- 1a — SELECT Z EMPIRICALLY. Do not assume one. ---

Z must be a third variant at which X's carriers are LARGELY CALLED. Measure it;
do not guess it.

mkdir -p /home/jupyter/occ_measure

python3 - <<'PYEOF'
import sys
sys.path.insert(0, "src/python")
from pairwise_completeness_scan import BedReader, iter_bim_windows

BFILE = "/home/jupyter/afr_cohort"
CHROM, XPOS = "15", 20394741
X_VID = "chr15:20394741:AT:A"
Y_VID = "chr15:20394743:T:C"
FLANK = 200
FLOOR = 0.80

rows = iter_bim_windows(BFILE + ".bim",
                        [("z", CHROM, XPOS - FLANK, XPOS + FLANK)])["z"]
print("variants within +/-%d bp of X: %d" % (FLANK, len(rows)))
idx_by_vid = dict((r[1], i) for i, r in rows)
assert X_VID in idx_by_vid, "X not found in the window .bim -- STOP"
assert Y_VID in idx_by_vid, "Y not found in the window .bim -- STOP"

reader = BedReader(BFILE)
gx = reader.read_variant(idx_by_vid[X_VID])
dx, cx = gx.dosage, gx.called
n_called_x = int(cx.sum())
af = float(dx[cx].sum()) / (2.0 * n_called_x)
xcar = ((dx >= 1) & cx) if af < 0.5 else ((dx >= 0) & (dx <= 1) & cx)
n_x = int(xcar.sum())
print("X %s: n_called %d  af_a1 %.6f  minor-allele carriers %d"
      % (X_VID, n_called_x, af, n_x))
assert n_x > 0, "X has no carriers -- STOP"

table = []
for i, r in rows:
    vid, pos = r[1], int(r[3])
    if vid in (X_VID, Y_VID):
        continue
    g = reader.read_variant(i)
    ret = float((xcar & g.called).sum()) / n_x
    table.append((ret, vid, pos, int(g.called.sum())))
reader.close()
table.sort(reverse=True)

print("%-36s %10s %10s %10s" % ("candidate Z", "pos", "n_called", "retention"))
for ret, vid, pos, nc in table:
    print("%-36s %10d %10d %10.4f" % (vid, pos, nc, ret))

assert table, "no candidate Z within the flank -- STOP"
best_ret, Z_VID, Z_POS, _nc = table[0]
print("")
print("CHOSEN Z = %s at %d, MEASURED retention %.4f (floor %.2f)"
      % (Z_VID, Z_POS, best_ret, FLOOR))
assert best_ret >= FLOOR, (
    "NO CANDIDATE CLEARS THE RETENTION FLOOR (best %.4f < %.2f) -- STOP AND "
    "REPORT. Without a Z at which X's carriers are largely called the "
    "discriminator has NO POWER, and running it anyway would manufacture a "
    "false falsification of a possibly-sound instrument." % (best_ret, FLOOR))
open("/home/jupyter/occ_measure/falsifier_Z.txt", "w").write(Z_VID + "\n")
print("wrote /home/jupyter/occ_measure/falsifier_Z.txt")
PYEOF

PASTE BACK: the whole retention table, the chosen Z and its MEASURED retention.
Every later step quotes that number.

⚠ ONE LINE OF HONESTY: 1a uses the instrument's OWN `.bed` decoder, so a decoder
bug could mis-select Z. That failure mode is FAIL-SAFE — it produces a false STOP,
never false confidence — and step 1c's 2-variant control distinguishes it from a
real falsification. It is not circular in the direction that matters.

--- 1b — THREE plink RUNS, production LD modifiers. ---

Z=$(cat /home/jupyter/occ_measure/falsifier_Z.txt)
printf 'chr15:20394741:AT:A\nchr15:20394743:T:C\n%s\n' "$Z" > /home/jupyter/occ_measure/falsifier_xyz.txt
printf 'chr15:20394741:AT:A\n%s\n'                      "$Z" > /home/jupyter/occ_measure/falsifier_xz.txt
printf 'chr15:20394741:AT:A\nchr15:20394743:T:C\n'           > /home/jupyter/occ_measure/falsifier_xy.txt
cat /home/jupyter/occ_measure/falsifier_xyz.txt

for TAG in xyz xz xy; do
  plink1.9 --bfile /home/jupyter/afr_cohort \
    --extract /home/jupyter/occ_measure/falsifier_${TAG}.txt \
    --keep-allele-order --mac 1 --nonfounders --write-snplist \
    --r square bin4 \
    --out /home/jupyter/occ_measure/falsifier_${TAG}
done

wc -l /home/jupyter/occ_measure/falsifier_xyz.snplist /home/jupyter/occ_measure/falsifier_xz.snplist /home/jupyter/occ_measure/falsifier_xy.snplist
ls -l /home/jupyter/occ_measure/falsifier_xyz.ld.bin /home/jupyter/occ_measure/falsifier_xz.ld.bin /home/jupyter/occ_measure/falsifier_xy.ld.bin

THE MODIFIER DECISIONS, AND WHY — so the experiment is auditable:

* `--keep-allele-order`, `--nonfounders`, `--r square bin4` — the PRODUCTION
  semantics, verbatim from `aou_ld_panel.build_plink_ld_command`'s square branch.
  These are the point of the experiment and none of them may be dropped.
* `--mac 1` — INCLUDED. It is a variant-DROP filter, not a correlation-semantics
  change, and all three variants are polymorphic cohort-wide, so it must be a
  NO-OP here. It is included precisely so the command is production-shaped, and
  the `.snplist` LINE COUNT is what PROVES the no-op (3 / 2 / 2 lines). If any
  run's `.snplist` is short: STOP. A dropped variant means the matrix is not the
  shape assumed and the read below would be MIS-INDEXED.
* `--exclude` (the occlusion manifest) — OMITTED, deliberately. It removes
  variants, i.e. it changes which pairs EXIST; it does not change how `r` is
  computed over a pair that does exist. The falsifier tests the COMPUTATION.
* `--chr/--from-bp/--to-bp` replaced by `--extract` — same reasoning: variant
  SELECTION is not correlation SEMANTICS. `--extract` rather than `--snps` because
  the ids contain colons and `--snps` parses `-` as a range separator; production
  itself selects variants from a FILE (via `--exclude`).

⚠ **READ THE `.snplist` FIRST, ALWAYS.** The `.ld.bin` rows are in `.bim` /
POSITION order, not in the order the ids were written to the extract file. If Z
sits before X on the chromosome then **Z is ROW 0**. Derive every row index FROM
THE SNPLIST before reshaping anything.

⚠ Do NOT import `read_square_bin` from `src/python/run_native_ld_panel.py`. It
RAISES on NaN by design, and NaN is the SIGNAL here. Use a plain `np.fromfile`.

--- 1c — DISCRIMINATE. ---

python3 - <<'PYEOF'
import os
import numpy as np

X = "chr15:20394741:AT:A"
Y = "chr15:20394743:T:C"
Z = open("/home/jupyter/occ_measure/falsifier_Z.txt").read().strip()
print("X =", X)
print("Y =", Y)
print("Z =", Z)

EXPECT_K = {"xyz": 3, "xz": 2, "xy": 2}
mats = {}
for tag in ("xyz", "xz", "xy"):
    k = EXPECT_K[tag]
    base = "/home/jupyter/occ_measure/falsifier_" + tag
    ids = [l.strip() for l in open(base + ".snplist") if l.strip()]
    assert len(ids) == k, (
        "SNPLIST LENGTH %d != %d for run %s -- a variant was DROPPED, so --mac 1 "
        "was NOT a no-op, the matrix is not the shape assumed and the read would "
        "be mis-indexed. STOP." % (len(ids), k, tag))
    nbytes = os.path.getsize(base + ".ld.bin")
    assert nbytes == k * k * 4, (
        "LD.BIN SIZE %d != %d (k*k*4) for run %s -- STOP." % (nbytes, k * k * 4, tag))
    m = np.fromfile(base + ".ld.bin", dtype="<f4").reshape(k, k)
    mats[tag] = (ids, m)
    print("")
    print("--- run %s, snplist ROW ORDER: %s" % (tag, ids))
    print(m)
    for i in range(k):
        d = float(m[i, i])
        assert abs(d - 1.0) < 1e-5, (
            "DIAGONAL %r at row %d of run %s is not 1.0 -- unclassified, STOP."
            % (d, i, tag))

def cell(tag, a, b):
    ids, m = mats[tag]
    return float(m[ids.index(a), ids.index(b)])

def nan(v):
    return v != v

def show(v):
    return "NaN" if nan(v) else ("%.6f" % v)

xy3, xz3, yz3 = cell("xyz", X, Y), cell("xyz", X, Z), cell("xyz", Y, Z)
xz2, xy2 = cell("xz", X, Z), cell("xy", X, Y)
print("")
print("OBSERVED  3-var(X,Y)=%s  3-var(X,Z)=%s  3-var(Y,Z)=%s  2-var(X,Z)=%s  2-var(X,Y)=%s"
      % (show(xy3), show(xz3), show(yz3), show(xz2), show(xy2)))
print("")
print("| hypothesis                        | 3-var (X,Y) | 3-var (X,Z) | 3-var (Y,Z) | 2-var (X,Z) | 2-var (X,Y) |")
print("|-----------------------------------|-------------|-------------|-------------|-------------|-------------|")
print("| pairwise-complete (ASSUMED)       | NaN         | finite      | finite      | finite      | NaN         |")
print("| mean-imputation                   | finite      | finite      | finite      | finite      | finite      |")
print("| listwise over the window          | NaN         | NaN         | finite      | finite      | NaN         |")
print("| Z mis-selected (X invar in X&Z)   | NaN         | NaN         | finite      | NaN         | NaN         |")
print("")

if nan(xy3) and not nan(xz3) and not nan(yz3) and not nan(xz2) and nan(xy2):
    verdict = "PAIRWISE-COMPLETE"
elif not any(map(nan, (xy3, xz3, yz3, xz2, xy2))):
    verdict = "MEAN-IMPUTATION"
elif nan(xy3) and nan(xz3) and not nan(yz3) and not nan(xz2) and nan(xy2):
    verdict = "LISTWISE-OVER-THE-WINDOW"
elif nan(xy3) and nan(xz3) and not nan(yz3) and nan(xz2) and nan(xy2):
    verdict = "Z-MIS-SELECTED"
else:
    verdict = "UNCLASSIFIED"
print("VERDICT:", verdict)
PYEOF

THE DISCRIMINATOR IS THE **2-variant (X,Z)** CELL. Real listwise-over-the-window
makes `(X,Z)` NaN when THREE variants are in the run (Y's missingness removes X's
carriers from the analysis set) and FINITE when only TWO are (the window shrank
and Y is gone). A merely MIS-SELECTED Z makes `(X,Z)` NaN in BOTH runs, because X
is genuinely invariant within `called(X) & called(Z)` regardless of Y. Without
that 2-variant run the two are indistinguishable — so a false alarm cannot
silently kill a valid sweep, and a real falsification cannot be explained away as
a bad Z.

Any pattern that is not one of the four rows is UNCLASSIFIED and is ITSELF A STOP.
A non-1.0 diagonal anywhere is a STOP.

--- 1d — THE CONSEQUENCE, explicit. ---

⛔ IF THE VERDICT IS ANYTHING OTHER THAN `PAIRWISE-COMPLETE`:
   **STOP. Paste everything verbatim. DISCARD THE SWEEP. Do NOT run STEP 2. Do
   NOT run STEP 3.** The instrument's premise is falsified and the whole approach
   needs rethinking before ANY number is generated. Do NOT adjust the code, the
   window, the choice of Z, or the expectations to make it pass. A wrong
   instrument does not produce a slightly wrong prevalence; it produces a
   confidently wrong one, and this one's numbers are headed for a public
   pre-registration.

EGRESS FROM STEP 1: the two/three matrices (9 + 4 + 4 floats), the three snplist
line counts, the chosen Z with its measured retention, and the retention table —
counts, coordinates and correlations only. Nothing per-sample.

=== STEP 2 — THE 00057 HARNESS CROSS-CHECK, before the sweep. ===

Only after STEP 1 prints VERDICT: PAIRWISE-COMPLETE.

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
                             "del_minor_allele_tie", "del_globally_invariant",
                             "partner_globally_invariant",
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
DISCARD ALL RESULTS. Do NOT run STEP 3. Do NOT adjust the expected numbers, the
window, or the code to make it pass.** A harness that disagrees with the one pair
we measured by hand is broken, and every number it would produce is worthless.
(This mirrors the region-1 `231` cross-check that guarded the site-basis sweep.)

=== STEP 2b — ROTATE the prior artifacts. Never delete. ===

THE 2026-08-26 SWEEP'S OUTPUT IS STILL SITTING AT THE PATHS THIS SWEEP WRITES.
`/home/jupyter/occ_measure/pcs_pairs.tsv` is 871,038,152 B / 2,865,514 lines and
every count in it is CONTAMINATED (the ancestry-blind 8x read). It is at exactly
the path STEP 3 later `wc -l`s. Move it aside BEFORE the sweep, so no stale byte
can be read as a fresh result.

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
for f in /home/jupyter/occ_measure/pcs_pairs.tsv /home/jupyter/occ_measure/pcs_summary.json; do
  if [ -e "$f" ]; then mv -v "$f" "$f.STALE.$STAMP"; fi
done
ls -l --time-style=full-iso /home/jupyter/occ_measure/

NEVER `rm`. The contaminated artifacts are EVIDENCE — they are the physical record
of the 8x defect, in exactly the same class as the forensic
`m2_region_00057.ld.bin`, and a later question about that run can only be answered
from the bytes. Project ruling:
`.planning/debug/260824-STAGE-A-env-stop-plink1.9-and-stale-scratch-TSV.md`
("ROTATE, never delete").

DISK: the rotate KEEPS the 871 MB copy and the sweep then writes a NEW artifact
beside it. STEP 0's `df -h /home/jupyter` must show room for BOTH. If it does not,
STOP and say so — do not free space by discarding the evidence.

PASTE BACK: the `mv -v` lines (or "nothing to rotate") and the `ls -l` listing,
including the `$STAMP` value. STEP 3's artifacts must later carry an mtime that
POST-DATES that stamp.

=== STEP 3 — THE SWEEP over the pre-committed 21-region sample. ===

Only after STEP 1 printed VERDICT: PAIRWISE-COMPLETE, STEP 2 printed
CROSS-CHECK PASSED, and STEP 2b rotated the prior artifacts.

python3 - <<'EOF'
import os, subprocess, sys
OUT = "/home/jupyter/occ_measure/pcs_pairs.tsv"
SUMMARY = "/home/jupyter/occ_measure/pcs_summary.json"
# PRE-FLIGHT. A stale artifact at an output path is EXACTLY how a contaminated
# file masqueraded as a fresh result on 2026-08-26: the operator's wc -l returned
# 2,865,514 from the PREVIOUS run. Refuse to start rather than risk it.
for path in (OUT, SUMMARY):
    if os.path.exists(path):
        raise SystemExit(
            "PRE-FLIGHT STOP: %s already exists. Run STEP 2b (ROTATE) first; do "
            "not overwrite it and do not discard it." % path)
SAMPLE = "/home/jupyter/occ_measure/occ_measure_sample.tsv"
ids = [l.split("\t")[0] for l in open(SAMPLE).read().splitlines()[1:] if l.strip()]
print("regions in the pre-committed sample:", len(ids))
# NAME them, do not merely count them: a count of 21 is satisfiable by the WRONG
# 21 (feedback_aggregate_agreement_hides_component_errors).
for rid in ids:
    print("  region id:", rid)
cmd = [sys.executable, "src/python/pairwise_completeness_scan.py",
       "--bfile-prefix", "/home/jupyter/afr_cohort",
       "--regions-tsv", "config/ld_regions.tsv",
       "--region-ids", ",".join(ids),
       "--window-bp", "25",
       "--out", OUT,
       "--summary", SUMMARY]
print(" ".join(cmd), flush=True)
raise SystemExit(subprocess.call(cmd))
EOF

wc -l /home/jupyter/occ_measure/pcs_pairs.tsv
ls -l --time-style=full-iso /home/jupyter/occ_measure/pcs_pairs.tsv /home/jupyter/occ_measure/pcs_summary.json

⚠ IF THE SWEEP EXITS 2 WITH A `POOLED denominator disagreement` LINE: the output
has been QUARANTINED to `/home/jupyter/occ_measure/pcs_pairs.tsv.SUSPECT` (and the
summary likewise) and NOTHING is left at the output path, so the `wc -l` above
will fail. That is the DESIGNED behaviour: the ~4h18m of compute is preserved in
the `.SUSPECT` files for forensics, and no plausible-looking artifact survives
where a fresh result belongs. STOP and paste the ERROR line and the `ls -l`
verbatim. Do not re-run over it.

PASTE BACK: the FULL stdout of the sweep (the per-region summary table, the pooled
offset histogram, the pooled lost-frac bins), the 21 NAMED region ids printed
above, that `wc -l` line, the `ls -l --time-style=full-iso` lines for BOTH new
artifacts, plus the contents of /home/jupyter/occ_measure/pcs_summary.json.

The `ls -l` lines are not decoration: their mtimes must POST-DATE the `$STAMP`
recorded in STEP 2b. A stale file must not be able to masquerade as fresh output.

=== EGRESS RULE ===

AGGREGATE COUNTS, FRACTIONS and VARIANT COORDINATES/IDS ONLY may cross back.
NEVER per-sample data of any kind. The full per-pair TSV
(/home/jupyter/occ_measure/pcs_pairs.tsv) STAYS IN-PERIMETER — do not paste it,
do not copy it out. The summary JSON, the stdout table and STEP 1's small matrices
are the deliverables. The falsifier's working files
(/home/jupyter/occ_measure/falsifier_*) also stay in-perimeter; only their line
counts and the 2x2 / 3x3 matrices cross.

=== OPERATIONAL NOTES ===

* The VM must be STARTED by Carter and STOPPED by Carter after. An agent NEVER
  fires anything billable without Carter's explicit go.
* `export PATH="$HOME/bin:$PATH"` is PER-SHELL and must be re-issued in each new
  terminal. It is **ON this sweep's critical path**: STEP 1 calls plink1.9 three
  times on 2-3 variants. STEPS 2 and 3 call no plink.
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

STEP 1 first: it is a PASS/STOP gate, not a measurement to interpret. Anything but
`PAIRWISE-COMPLETE` means the sweep is discarded and the approach is rethought.

Then the three OPEN questions and the field that speaks to each. **No expected
value is stated for any of them, deliberately** — see the sweep design in the halt
record § "PREVALENCE SWEEP".

| OPEN question | The field that measures it |
|---|---|
| (a) prevalence of undefined pairs | `n_undefined_distinct_pairs`, split into `n_undefined_already_occluded` (the posted rule already covers these) vs `n_undefined_not_already_occluded` (the NEWLY DISCOVERED class) |
| (b) the true boundary width, and whether it is one-sided | `undefined_offset_histogram` — the empirical offset distribution over the undefined set, swept on BOTH sides. NEGATIVE offsets are upstream of `pos`; a nonempty negative side would mean the posted one-sided rule under-covers in a second direction. |
| (c) whether a partial-confounding tail exists | `defined_carriers_lost_frac_bins` and `n_defined_lost_frac_ge_0p9` over DEFINED rows — finite-`r` pairs computed on carrier-depleted subsamples, which no NaN check anywhere in the pipeline can see |

Three counters exist so the numbers can be SUBTRACTED rather than argued about:
`n_candidates_edge_clipped` (pairs the region boundary suppressed — correct, but
now visible), `n_globally_invariant_variants` and
`n_undefined_rows_with_globally_invariant_member` (the `--mac 1` retained-set
parity class, which would OVER-report undefined pairs relative to a matrix that
never contained those variants).

Region 1 is the negative control already in hand: 102,421 in-window rows, 7,951
multi-base-REF rows, 38,595,391,746 bytes re-read, ZERO NaN. That establishes only
that region 1 held no *perfectly* confounded pair — **not** that it is free of
deletion-linked missingness bias. Column (c) is the first instrument able to tell
those two apart.
