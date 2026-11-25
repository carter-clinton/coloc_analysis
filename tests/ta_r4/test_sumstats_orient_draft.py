"""N1 eligibility re-measured on the oriented r4 sumstats, and the DRAFT's orientation, collector-audit and eligibility
numbers re-derived from the manifests (W3f 15.8a4; Carter Q-158R2 D, Q-158OR A, Q-158PAL A, Q-158EL A;
DEC-2026-11-25-ta-r4-sumstats-orientation)."""
from __future__ import annotations

import csv
import hashlib

from .conftest import MAN_DIR, REPO_ROOT

from ta_r4 import arms, paths  # noqa: E402

CAP = 16000
ELIG = MAN_DIR / "w3f_fit_eligibility.tsv"
ORIENT = MAN_DIR / "sumstats_r4_orientation.tsv"
SUMSTATS_PINS = MAN_DIR / "sumstats_r4_sha256.tsv"
#: Typed copy of the table pinned before 15.8a4 (manifests/w3f_fit_eligibility.tsv at 14a9d265).
PRE = REPO_ROOT / "data/r4/tmp/w3f/q158/a4/w3f_fit_eligibility.pre.tsv"
PRE_SHA256 = "4a07d89cfee3cd359e0bef371b7b1fcce14661114a446b7b98dbcdf698cc3208"
#: The fits Carter was shown in Q-158EL as going over the cap on the oriented inputs (eligible true -> false).
Q158EL_SET = {("AFR661_A3", "t2d", "AFR", "BMI_5q13_3"), ("AFR661_A2", "t2d", "AFR", "BMI_5q13_3"),
              ("AFR504_A3", "t2d", "AFR", "BMI_5q13_3")}
UNFLIPPED = {("bmi", "EUR"), ("t2d", "EUR")}


def _rows(p):
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _keyed(rows):
    return {(r["arm"], r["trait"], r["ancestry"], r["region_safe"]): r for r in rows}


def test_eligibility_on_oriented_inputs_reconciles():
    assert hashlib.sha256(PRE.read_bytes()).hexdigest() == PRE_SHA256
    pre, new = _keyed(_rows(PRE)), _keyed(_rows(ELIG))
    assert len(pre) == len(new) == 815 and set(pre) == set(new)
    measured = {k for k, r in pre.items() if r["method"] == "measured"}
    assert len(measured) == 83 and measured == {k for k, r in new.items() if r["method"] == "measured"}
    orient = {(r["region_safe"], r["trait"], r["ancestry"]): int(r["after_exact"]) + int(r["after_both"])
              for r in _rows(ORIENT)}
    for k in sorted(new):
        p, n = pre[k], new[k]
        if k not in measured:
            # (a) a bound row moves only in the sha256 of the sumstats it reads
            assert {c: v for c, v in n.items() if c != "sumstats_sha256"} == \
                   {c: v for c, v in p.items() if c != "sumstats_sha256"}, k
            assert int(n["panel_n_var"]) <= CAP and n["eligible"] == "true", k
            continue
        assert (n["catalog_sha256"], n["panel_sha256"], n["panel_n_var"]) == \
               (p["catalog_sha256"], p["panel_sha256"], p["panel_n_var"]), k
        pre_ld, nv = int(n["n_variants_pre_ld"]), int(n["n_variants"])
        d_pre, d_n = pre_ld - int(p["n_variants_pre_ld"]), nv - int(p["n_variants"])
        if (k[1], k[2]) in UNFLIPPED:  # (b)
            assert (d_pre, d_n, n["sumstats_sha256"] != p["sumstats_sha256"]) == (0, 0, True), k
        assert pre_ld == orient[(k[3], k[1], k[2])], k  # (c)
        assert d_n >= 0, k  # (d)
        assert d_n <= d_pre, k  # (e)
        assert n["status"] == "too_many_variants" and n["cap_stage"] == "after_ld_restriction", k
        assert n["eligible"] == str(nv <= CAP).lower(), k
    changed = {k for k in new if new[k]["eligible"] != pre[k]["eligible"]}
    assert changed == Q158EL_SET
    assert all((pre[k]["eligible"], new[k]["eligible"]) == ("true", "false") for k in changed)


def test_eligibility_manifest_records_the_oriented_sumstats():
    pins = {r["path"]: r["sha256"] for r in _rows(SUMSTATS_PINS)}
    rows = _rows(ELIG)
    assert len(rows) == 815
    seen = set()
    for r in rows:
        sp = paths.sumstats_path(r["trait"], r["ancestry"], r["arm"])
        assert arms.ARMS[r["arm"]]["route"] == "r4" and sp == paths.oriented_sumstats_path(r["trait"], r["ancestry"])
        assert r["sumstats_sha256"] == pins[sp], (r["arm"], r["trait"], r["ancestry"], r["region_safe"])
        seen.add(sp)
    assert len(seen) == 8


DRAFT = REPO_ROOT / ".planning/amendments/osf-amendment-r4-DRAFT.md"
FIXED_POINT = MAN_DIR / "catalogs_r4_fixed_point.tsv"
COLLECTOR = MAN_DIR / "catalog_collector_drops.tsv"
#: (c)'s inputs list order and labels.
INPUTS = [("asthma", "EUR", "asthma EUR"), ("asthma", "AFR", "asthma AFR"), ("bmi", "EUR", "BMI EUR"),
          ("hypertension", "EUR", "hypertension EUR"), ("stroke", "EUR", "stroke EUR"),
          ("stroke", "AFR", "stroke AFR"), ("t2d", "EUR", "type 2 diabetes EUR"),
          ("t2d", "AFR", "type 2 diabetes AFR")]
OLD_INPUTS = ("Inputs (sha256 recorded before production and verified inside every production fit, colocalization and "
              "QTL job for the summary statistics, variant catalogs and harmonized QTL files it reads; a mismatch or an "
              "unlisted input fails the job):")
NEW_INPUTS = ("Inputs (sha256 recorded before production; production jobs read the oriented copies of these summary "
              "statistics listed below, and every production fit, colocalization and QTL job verifies the sha256 of "
              "those copies, the variant catalogs and the harmonized QTL files it reads; a mismatch or an unlisted "
              "input fails the job):")
OLD_COLLECTION = ("the collection step before it keeps one row per rsid and omits unnamed variants at a position that "
                  "carries an rsid, without an audit")


def _para(prefix):
    lines = [ln for ln in DRAFT.read_text().splitlines() if ln.startswith(prefix)]
    assert len(lines) == 1, prefix
    return lines[0]


def _once(text, s):
    assert text.count(s) == 1, s


def test_draft_orientation_sentence_matches_the_manifests():
    o = _rows(ORIENT)
    regions = {r["region_safe"] for r in o}
    flips = {(t, a): sum(int(r["n_flipped"]) for r in o if (r["trait"], r["ancestry"]) == (t, a)) for t, a, _ in INPUTS}
    n_pal = sum(int(r["n_flipped_palindromic"]) for r in o)
    assert sum(int(r["after_swapped_only"]) for r in o) == 0
    assert sum(flips.values()) == sum(int(r["swapped_only"]) for r in o)
    fp = _rows(FIXED_POINT)
    assert {r["region_safe"] for r in fp} == regions
    n_fp = sum(r["equal"] == "true" for r in fp)
    c = _para("(c) **Data.**")
    per = ", ".join(f"{lab} {flips[(t, a)]:,}" for t, a, lab in INPUTS)
    _once(c, f"({sum(flips.values()):,} rows in the {len(regions)} regions: {per}; A/T and C/G SNPs, {n_pal:,} of "
             "them, are treated the same way and are dropped from the fits by the allele-aware panel join;")
    _once(c, "keeps them), after which no row matches the catalog only the other way round; rebuilt from these files, "
             f"{n_fp} of {len(regions)} catalogs are byte-identical, so no catalog or panel changed.")
    assert (len(regions), n_fp) == (31, 31)
    _once(_para("(i) **Allele orientation.**"), "In R4, EUR panels carry REF/ALT, summary statistics are first put in "
                                                "the variant catalog's orientation ((c)), the EUR join is allele-aware")


def test_draft_collection_clause_matches_the_collector_audit():
    d = _rows(COLLECTOR)
    n_drop = sum(int(r["n_dropped"]) for r in d)
    assert n_drop == sum(int(r["audit_rows"]) for r in d)
    lost = sum(int(r["n_lost_keys"]) for r in d)
    swapped = sum(int(r["n_lost_keys_swapped_present"]) for r in d)
    assert swapped == sum(int(r["n_flipped"]) for r in _rows(ORIENT))
    c = _para("(c) **Data.**")
    assert OLD_COLLECTION not in c
    _once(c, f"replaying that step on the same inputs ({n_drop:,} rows over {len(d)} regions; {lost:,} of them with an "
             f"allele key that is not in the catalog: {swapped:,} the same variant written the other way round, which "
             f"the orientation step restores, and {lost - swapped:,} with an allele pair the catalog does not hold, "
             "which are not fitted)")
    assert (n_drop, len(d), lost, swapped, lost - swapped) == (722928, 31, 162724, 159969, 2755)


def test_draft_inputs_list_the_oriented_sha256():
    pins = {r["path"]: r["sha256"] for r in _rows(SUMSTATS_PINS)}
    c = _para("(c) **Data.**")
    assert OLD_INPUTS not in c and "verified inside every production fit" not in c
    _once(c, NEW_INPUTS)
    listed = "; ".join(f"{lab} `{pins[paths.oriented_sumstats_path(t, a)]}`" for t, a, lab in INPUTS)
    _once(c, "Production jobs read, and verify by sha256 in every production job, copies of these files written in "
             f"the variant catalog's allele orientation (below): {listed}.")
    for t, a, _ in INPUTS:
        _once(c, pins[paths.oriented_sumstats_path(t, a)])


def test_draft_eligibility_counts_match_the_manifest():
    rows = _rows(ELIG)
    order = []
    for r in rows:
        if r["arm"] not in order:
            order.append(r["arm"])
    per = {a: (sum(r["eligible"] == "false" for r in rows if r["arm"] == a), sum(r["arm"] == a for r in rows))
           for a in order}
    assert all(per[a][0] == 0 for a in order if all(r["method"] == "bound" for r in rows if r["arm"] == a))
    orient = {(r["region_safe"], r["trait"], r["ancestry"]): int(r["after_exact"]) + int(r["after_both"])
              for r in _rows(ORIENT)}
    meas = [r for r in rows if r["method"] == "measured"]
    m = sum(int(r["n_variants_pre_ld"]) == orient[(r["region_safe"], r["trait"], r["ancestry"])] for r in meas)
    row = _para("| Measured post-restriction counts")
    text = "; ".join(f"{a} {k} of {n}" for a, (k, n) in per.items())
    _once(row, f"above 16,000: {text}; total {sum(k for k, _ in per.values())}; pre-LD rows equal the orientation "
               f"manifest in {m}/{len(meas)} measured fits.")
    assert m == len(meas) == 83
