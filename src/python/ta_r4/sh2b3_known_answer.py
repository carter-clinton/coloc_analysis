"""W3b SH2B3 known answer (D-17): R2-exact coloc per pair vs the frozen R2 JSONs; the L10/iter-100 run is a
separate measurement and is never compared to the known answer. Mismatches are findings (§B.10).

  python -m ta_r4.sh2b3_known_answer [--out $MAN/known_answer_sh2b3.tsv]   (cwd = repo root)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
from pathlib import Path

from ta_r4 import paths

TOL = 1e-6
FROZEN_DIR = "results/multitrait/coloc_susie_R2"
REPRO_DIRS = {"R2_exact": f"{paths.R4}/results/repro_sh2b3_r2/coloc",
              "L10_iter100": f"{paths.R4}/results/repro_sh2b3_L10/coloc"}
OUT = f"{paths.MAN}/known_answer_sh2b3.tsv"
R1_OUT = f"{paths.MAN}/r1_structural_crosscheck.tsv"
FIT_CS_OUT = f"{paths.MAN}/fit_cs_json_vs_rds.tsv"
R1_TARGETS = ".planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv"
W3A_TABLE = f"{paths.MAN}/known_answer_W3a.tsv"
RSCRIPT = os.environ.get("R4_RSCRIPT", "Rscript")
PAIRS = tuple(f"SH2B3_12q24__EUR__{p}" for p in (
    "asthma_vs_bmi", "asthma_vs_hypertension", "asthma_vs_stroke", "bmi_vs_hypertension", "bmi_vs_stroke",
    "bmi_vs_t2d", "hypertension_vs_stroke", "hypertension_vs_t2d", "stroke_vs_t2d"))
#: ta-sh2b3-W2-canonical-pair-coloc-susie-SUMMARY.md:102 (D6).
FINGERPRINT = {"pair_id": "SH2B3_12q24__EUR__bmi_vs_hypertension",
               "n_cs_a": 13, "n_cs_b": 5, "nsnps": 168, "hit1": "rs3184504", "hit2": "rs3184504"}
#: n_CS: ta-sh2b3-W1-convergence-report.tsv (L15, niter 1000); ld_overlap: the surviving L15 lsweep JSONs.
L15_EXPECTED = {"bmi": (13, 170), "hypertension": (5, 589), "stroke": (3, 622)}
FP_FIELDS = ("nsnps", "hit1", "hit2", "n_cs_a", "n_cs_b")
COLUMNS = ["config_label", "pair_id", "status", "status_frozen", "pp_h4_reproduced", "pp_h4_frozen", "abs_diff",
           "nsnps", "nsnps_frozen", "hit1", "hit2", "hit1_frozen", "hit2_frozen",
           "n_cs_a", "n_cs_b", "n_cs_a_frozen", "n_cs_b_frozen", "fingerprint_eq", "match_flag"]


def _fields(doc):
    s = doc.get("summary") or {}
    return {"status": doc.get("status"), "pp_h4": s.get("PP.H4.abf"), "nsnps": s.get("nsnps"),
            "hit1": s.get("hit1"), "hit2": s.get("hit2"), "n_cs_a": doc.get("n_cs_a"), "n_cs_b": doc.get("n_cs_b")}


def fingerprint_check(doc):
    """bmi_vs_hypertension field by field against the recorded R2 fingerprint."""
    f = _fields(doc)
    return {k: {"observed": f[k], "expected": FINGERPRINT[k], "eq": f[k] == FINGERPRINT[k]}
            for k in ("n_cs_a", "n_cs_b", "nsnps", "hit1", "hit2")}


def _num(x):
    return "NA" if x is None else f"{float(x):.6e}"


def compare_row(label, pair_id, rep, frozen):
    r, f = _fields(rep), _fields(frozen) if frozen is not None else None
    row = {"config_label": label, "pair_id": pair_id, "status": r["status"],
           "status_frozen": f["status"] if f else None, "pp_h4_reproduced": _num(r["pp_h4"]),
           "pp_h4_frozen": "NA", "abs_diff": "NA", "nsnps": r["nsnps"], "hit1": r["hit1"], "hit2": r["hit2"],
           "n_cs_a": r["n_cs_a"], "n_cs_b": r["n_cs_b"], "fingerprint_eq": None, "match_flag": None}
    for k in ("nsnps", "hit1", "hit2", "n_cs_a", "n_cs_b"):
        row[f"{k}_frozen"] = f[k] if f else None
    if f is not None:
        row["pp_h4_frozen"] = _num(f["pp_h4"])
        both = r["pp_h4"] is not None and f["pp_h4"] is not None
        diff = abs(float(r["pp_h4"]) - float(f["pp_h4"])) if both else None
        row["abs_diff"] = "NA" if diff is None else f"{diff:.3e}"
        pp_ok = (diff is not None and diff <= TOL) or (r["pp_h4"] is None and f["pp_h4"] is None)
        fp_ok = all(r[k] == f[k] for k in FP_FIELDS)
        if pair_id == FINGERPRINT["pair_id"]:
            fp_ok = fp_ok and all(v["eq"] for v in fingerprint_check(rep).values())
        row["fingerprint_eq"] = fp_ok
        row["match_flag"] = bool(pp_ok and fp_ok and r["status"] == f["status"])
    return {k: _str(row[k]) for k in COLUMNS}


def _str(x):
    if x is None:
        return "NA"
    if isinstance(x, bool):
        return "true" if x else "false"
    return str(x)


def _load(d, pair_id):
    return json.loads((Path(d) / f"{pair_id}.json").read_text())


def build_table(root=".", frozen_dir=None, repro_dirs=None):
    root = Path(root)
    frozen_dir = Path(frozen_dir) if frozen_dir else root / FROZEN_DIR
    repro_dirs = repro_dirs or {k: root / v for k, v in REPRO_DIRS.items()}
    rows = []
    for label in ("R2_exact", "L10_iter100"):
        for p in PAIRS:
            frozen = _load(frozen_dir, p) if label == "R2_exact" else None
            rows.append(compare_row(label, p, _load(repro_dirs[label], p), frozen))
    return rows


def l15_fit_check(fits):
    """fits: {trait: fit JSON doc} for the repro_sh2b3_r2 L15 fits; n_CS = len(credible_sets)."""
    out = []
    for t, (n_exp, ov_exp) in L15_EXPECTED.items():
        d = fits[t]
        n = len(d.get("credible_sets") or {})
        out.append({"trait": t, "n_cs": n, "n_cs_expected": n_exp, "n_cs_eq": n == n_exp,
                    "ld_overlap": d.get("ld_overlap"), "ld_overlap_expected": ov_exp,
                    "ld_overlap_eq": d.get("ld_overlap") == ov_exp,
                    "status": d.get("status"), "niter": d.get("niter"), "L_used": d.get("L_used")})
    return out


def r1_crosscheck(targets, n_cs):
    """targets: ta-r3-W2-r1-targets.tsv rows; n_cs: {(trait, ancestry, region_safe): n_CS}. KeyError if absent."""
    rows = []
    for t in targets:
        reg = t["base_region"]
        a, b = n_cs[(t["trait_a"], t["ancestry"], reg)], n_cs[(t["trait_b"], t["ancestry"], reg)]
        rows.append({"pair_id": t["pair_id"], "n_cs_a": a, "n_cs_b": b, "any_side_zero": a == 0 or b == 0})
    return rows


_SETS_R = r"""
for (p in commandArgs(TRUE)) {
  f <- readRDS(p)
  n <- if (is.list(f) && !is.null(f$sets)) length(f$sets$cs) else NA
  writeLines(paste(p, n, sep = "\t"))
}
"""


def rds_cs_counts(arm, keys):
    """{key: length(fit$sets$cs)} of the arm's .fit.rds (the sets coloc.susie reads); None without $sets."""
    rds = {k: paths.fit_rds(arm, *k) for k in keys}
    out = subprocess.run([RSCRIPT, "-e", _SETS_R, *rds.values()], check=True, capture_output=True, text=True).stdout
    by_path = dict(line.split("\t") for line in out.splitlines())
    return {k: None if by_path[p] == "NA" else int(by_path[p]) for k, p in rds.items()}


def fit_cs_table(w3a_rows, rds_counts):
    """Real-LD fits: JSON credible_sets count (W3a n_cs_L) vs length(fit$sets$cs)."""
    rows = []
    for r in w3a_rows:
        if r["pair"] != "real_ld":
            continue
        k = (r["trait"], r["ancestry"], r["region_safe"])
        rds = rds_counts[k]
        rows.append({"trait": k[0], "ancestry": k[1], "region_safe": k[2], "status": r["status_L"],
                     "n_cs_json": r["n_cs_L"], "n_cs_rds_sets": _str(rds),
                     "eq": "NA" if rds is None else _str(int(r["n_cs_L"]) == rds)})
    return rows


def r1_table(targets, json_n, rds_n):
    j, d = r1_crosscheck(targets, json_n), r1_crosscheck(targets, rds_n)
    return [{"pair_id": a["pair_id"], "n_cs_json_a": a["n_cs_a"], "n_cs_json_b": a["n_cs_b"],
             "any_zero_json": _str(a["any_side_zero"]), "n_cs_rds_a": _str(b["n_cs_a"]),
             "n_cs_rds_b": _str(b["n_cs_b"]), "any_zero_rds": _str(b["any_side_zero"])} for a, b in zip(j, d)]


def _read_tsv(p):
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_table(rows, out, columns=COLUMNS):
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    rows = build_table()
    write_table(rows, a.out)
    r2 = [r for r in rows if r["config_label"] == "R2_exact"]
    print(f"rows {len(rows)} (R2_exact {len(r2)} + L10_iter100 {len(rows) - len(r2)}); "
          f"R2_exact match {sum(r['match_flag'] == 'true' for r in r2)} + "
          f"differ {sum(r['match_flag'] == 'false' for r in r2)} = {len(r2)}")
    print("fingerprint", json.dumps(fingerprint_check(_load(REPRO_DIRS["R2_exact"], FINGERPRINT["pair_id"]))))
    fits = {t: json.loads(Path(paths.fit_json("repro_sh2b3_r2", t, "EUR", "SH2B3_12q24")).read_text())
            for t in L15_EXPECTED}
    for r in l15_fit_check(fits):
        print("l15", json.dumps(r))

    w3a = _read_tsv(W3A_TABLE)
    keys = [(r["trait"], r["ancestry"], r["region_safe"]) for r in w3a if r["pair"] == "real_ld"]
    rds = rds_cs_counts("repro_routeL", keys)
    fc = fit_cs_table(w3a, rds)
    write_table(fc, FIT_CS_OUT, list(fc[0]))
    print(f"fit_cs: {len(fc)} fits; eq {sum(r['eq'] == 'true' for r in fc)} + differ "
          f"{sum(r['eq'] == 'false' for r in fc)} + no_sets {sum(r['eq'] == 'NA' for r in fc)}")
    json_n = {(r["trait"], r["ancestry"], r["region_safe"]): int(r["n_cs_L"]) for r in w3a if r["pair"] == "real_ld"}
    r1 = r1_table(_read_tsv(R1_TARGETS), json_n, rds)
    write_table(r1, R1_OUT, list(r1[0]))
    for col in ("any_zero_json", "any_zero_rds"):
        print(f"r1 {col}: true {sum(r[col] == 'true' for r in r1)} + false {sum(r[col] == 'false' for r in r1)}"
              f" = {len(r1)}")


if __name__ == "__main__":
    main()
