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
