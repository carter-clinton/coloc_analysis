"""W3a known-answer comparison (D-12b): Route C vs Route L per fit, each vs the frozen record.

Mismatches are findings (§B.10); nothing here tunes or filters toward the frozen numbers.

  python -m ta_r4.known_answer_compare [--out $MAN/known_answer_W3a.tsv]   (cwd = repo root)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
from collections import Counter
from pathlib import Path

from ta_r4 import commands, paths

TOL = 1e-10
RSCRIPT = os.environ.get("R4_RSCRIPT", "Rscript")  # the r_coloc env Rscript (paths stay out of src/)
ROUTE_PAIRS = {"real_ld": ("repro_routeC", "repro_routeL"), "k2d": ("repro_k2d_routeC", "repro_k2d_routeL")}
OUT = f"{paths.MAN}/known_answer_W3a.tsv"

#: TRACK-A-FROZEN-NUMBERS.md (Stage 2 real-LD, 2026-04-22 fire); the per-fit table is not on disk.
FROZEN_REAL_LD = {"n": 96, "non_empty": 51,
                  "status_counts": {"ok": 48, "too_many_variants": 24, "non_converged": 18, "no_variants": 6}}
#: The one per-fit real-LD value quoted in the frozen record (TRACK-A-FROZEN-NUMBERS.md:26).
FROZEN_REAL_LD_SPOT = {("bmi", "EUR", "APOE_19q13"): {"status": "non_converged", "n_CS": "6", "cs_sizes": None}}

COLUMNS = ["pair", "trait", "ancestry", "region_safe", "present_C", "present_L",
           "status_C", "status_L", "n_cs_C", "n_cs_L", "cs_sizes_C", "cs_sizes_L", "n_var_C", "n_var_L",
           "status_eq", "n_cs_eq", "cs_sizes_eq", "variant_ids_eq", "max_abs_dpip", "C_equiv_L",
           "ld_source_class_C", "ld_source_class_L",
           "frozen_source", "frozen_status", "frozen_n_cs", "frozen_cs_sizes",
           "C_status_eq_frozen", "C_n_cs_eq_frozen", "C_cs_sizes_eq_frozen",
           "L_status_eq_frozen", "L_n_cs_eq_frozen", "L_cs_sizes_eq_frozen"]


def compare(fit_c, fit_l, tol=TOL):
    """Per-fit Route C vs Route L. PIPs are aligned by variant id; differing id sets are reported, not filled."""
    r = {"status_eq": fit_c["status"] == fit_l["status"], "n_cs_eq": fit_c["n_cs"] == fit_l["n_cs"],
         "cs_sizes_eq": tuple(fit_c["cs_sizes"]) == tuple(fit_l["cs_sizes"]),
         "variant_ids_eq": None, "n_only_c": 0, "n_only_l": 0, "max_abs_dpip": None}
    pc, pl = fit_c.get("pip"), fit_l.get("pip")
    if pc is None or pl is None:
        r["variant_ids_eq"] = pc is None and pl is None
        pip_ok = r["variant_ids_eq"]
    else:
        r["n_only_c"], r["n_only_l"] = len(pc.keys() - pl.keys()), len(pl.keys() - pc.keys())
        r["variant_ids_eq"] = r["n_only_c"] == 0 and r["n_only_l"] == 0
        if r["variant_ids_eq"]:
            r["max_abs_dpip"] = max((abs(pc[k] - pl[k]) for k in pc), default=0.0)
        pip_ok = r["max_abs_dpip"] is not None and r["max_abs_dpip"] <= tol
    r["equal"] = bool(r["status_eq"] and r["n_cs_eq"] and r["cs_sizes_eq"] and pip_ok)
    return r


def _sizes(s):
    return tuple(int(x) for x in s.split(";") if x != "")


def compare_to_k2d(row, fit):
    """Equality flags of a fit vs one frozen summary row (IDENTITY-LD-K2D-FIT-SUMMARY.tsv columns)."""
    return {"status_eq": fit["status"] == row["status"], "n_cs_eq": fit["n_cs"] == int(row["n_CS"]),
            "cs_sizes_eq": tuple(fit["cs_sizes"]) == _sizes(row["cs_sizes"])}


def aggregate(fits):
    return {"n": len(fits), "non_empty": sum(1 for f in fits if f["n_cs"] > 0),
            "status_counts": dict(Counter(f["status"] for f in fits))}


def compare_aggregate(agg, frozen=FROZEN_REAL_LD):
    return {"n_eq": agg["n"] == frozen["n"], "non_empty_eq": agg["non_empty"] == frozen["non_empty"],
            "status_counts_eq": agg["status_counts"] == frozen["status_counts"]}


# ---------------------------------------------------------------- on-disk loading

def fit_dir(arm):
    return Path(paths.fit_json(arm, "x", "EUR", "x")).parent


def fit_ids_on_disk(arm):
    out = set()
    for p in fit_dir(arm).glob("*.json"):
        if p.name.endswith(".ld_receipt.json"):
            continue
        trait, anc, region = p.name[: -len(".json")].split(".")
        out.add((trait, anc, region))
    return out


_PIP_R = r"""
for (p in commandArgs(TRUE)) {
  f <- readRDS(p)
  if (!is.list(f) || is.null(f$pip)) next
  nm <- names(f$pip); if (is.null(nm)) nm <- paste0("#", seq_along(f$pip))
  writeLines(paste(p, nm, sprintf("%.17g", f$pip), sep = "\t"))
}
"""


def load_pips(rds_paths):
    """{rds_path: {variant_id: pip}} for every fit object with a pip vector (early exits have none)."""
    if not rds_paths:
        return {}
    out = subprocess.run([RSCRIPT, "-e", _PIP_R, *map(str, rds_paths)], check=True, capture_output=True,
                         text=True).stdout
    pips = {}
    for line in out.splitlines():
        p, v, x = line.split("\t")
        d = pips.setdefault(p, {})
        if v in d:
            raise ValueError(f"{p}: duplicate variant id {v}")
        d[v] = float(x)
    return pips


def load_fit(json_path, pips):
    d = json.loads(Path(json_path).read_text())
    cs = d.get("credible_sets") or {}
    sizes = tuple(len(v) for v in cs.values()) if isinstance(cs, dict) else ()
    rds = str(json_path)[: -len(".json")] + ".fit.rds"
    receipt = Path(str(json_path)[: -len(".json")] + ".ld_receipt.json")
    rc = json.loads(receipt.read_text()) if receipt.exists() else {}
    return {"status": d.get("status"), "n_cs": len(sizes), "cs_sizes": sizes, "pip": pips.get(rds),
            "ld_source_class": rc.get("ld_source_class", "NA")}


def load_arm(arm):
    ids = sorted(fit_ids_on_disk(arm))
    jsons = {k: paths.fit_json(arm, *k) for k in ids}
    rds = [j[: -len(".json")] + ".fit.rds" for j in jsons.values()]
    pips = load_pips([p for p in rds if Path(p).exists()])
    return {k: load_fit(j, pips) for k, j in jsons.items()}


# ---------------------------------------------------------------- table

def _s(x):
    if x is None:
        return "NA"
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, float):
        return f"{x:.3e}"
    if isinstance(x, tuple):
        return ";".join(map(str, x)) if x else "-"
    return str(x)


def _frozen(pair, key, k2d):
    if pair == "k2d":
        row = k2d.get(key)
        return ("IDENTITY-LD-K2D-FIT-SUMMARY.tsv", row) if row else ("absent_from_record", None)
    row = FROZEN_REAL_LD_SPOT.get(key)
    return ("TRACK-A-FROZEN-NUMBERS.md:26", row) if row else ("aggregate_only", None)


def _vs_frozen(row, fit):
    if row is None or fit is None:
        return (None, None, None)
    f = {"status_eq": fit["status"] == row["status"], "n_cs_eq": fit["n_cs"] == int(row["n_CS"]),
         "cs_sizes_eq": None if row["cs_sizes"] is None else tuple(fit["cs_sizes"]) == _sizes(row["cs_sizes"])}
    return (f["status_eq"], f["n_cs_eq"], f["cs_sizes_eq"])


def build_table(loaded=None):
    k2d = {(r["trait"], r["ancestry"], commands.safe_region_id(r["region_id"])): r for r in commands.k2d_record_rows()}
    loaded = loaded or {}
    rows = []
    for pair, (arm_c, arm_l) in ROUTE_PAIRS.items():
        fc = loaded[arm_c] if arm_c in loaded else load_arm(arm_c)
        fl = loaded[arm_l] if arm_l in loaded else load_arm(arm_l)
        for key in sorted(fc.keys() | fl.keys()):
            c, l = fc.get(key), fl.get(key)
            cmp_ = compare(c, l) if c and l else {}
            src, frow = _frozen(pair, key, k2d)
            vc, vl = _vs_frozen(frow, c), _vs_frozen(frow, l)
            vals = [pair, *key, c is not None, l is not None,
                    c and c["status"], l and l["status"], c and c["n_cs"], l and l["n_cs"],
                    c and c["cs_sizes"], l and l["cs_sizes"],
                    c and (len(c["pip"]) if c["pip"] is not None else None),
                    l and (len(l["pip"]) if l["pip"] is not None else None),
                    cmp_.get("status_eq"), cmp_.get("n_cs_eq"), cmp_.get("cs_sizes_eq"), cmp_.get("variant_ids_eq"),
                    cmp_.get("max_abs_dpip"), cmp_.get("equal", False),
                    c and c["ld_source_class"], l and l["ld_source_class"],
                    src, frow and frow["status"], frow and frow["n_CS"],
                    frow and (None if frow["cs_sizes"] is None else _sizes(frow["cs_sizes"])), *vc, *vl]
            rows.append(dict(zip(COLUMNS, map(_s, vals))))
    return rows


def summarize(rows):
    """Reconciled counts for the LOG: equal + differ == total for every comparison."""
    out = {}
    for pair in ROUTE_PAIRS:
        rs = [r for r in rows if r["pair"] == pair]
        eq = sum(r["C_equiv_L"] == "true" for r in rs)
        s = {"total": len(rs), "C_equiv_L": eq, "C_differs_L": len(rs) - eq}
        for route in ("C", "L"):
            for f in ("status", "n_cs", "cs_sizes"):
                col = [r[f"{route}_{f}_eq_frozen"] for r in rs]
                s[f"{route}_{f}_vs_frozen"] = dict(Counter(col))
            fits = [{"status": r[f"status_{route}"], "n_cs": int(r[f"n_cs_{route}"])}
                    for r in rs if r[f"present_{route}"] == "true"]
            agg = aggregate(fits)
            s[f"{route}_aggregate"] = agg
            if pair == "real_ld":
                s[f"{route}_aggregate_vs_frozen"] = compare_aggregate(agg)
        out[pair] = s
    return out


def write_table(rows, out=OUT):
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, COLUMNS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    rows = build_table()
    write_table(rows, a.out)
    print(json.dumps(summarize(rows), indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
