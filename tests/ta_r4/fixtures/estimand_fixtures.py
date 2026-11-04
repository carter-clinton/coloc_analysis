"""Synthetic coloc JSON docs and pair-manifest rows for the W3d estimand / aggregation tests."""
from __future__ import annotations

import random

import pandas as pd

MANIFEST_COLS = ["row_id", "ancestry", "region_id", "region_safe", "trait_a", "trait_b", "row_class",
                 "admissible", "inadmissible_reason", "canonical_pair", "nc_set", "nc_caveat"]
PAIRS = [("asthma", "bmi"), ("asthma", "t2d"), ("bmi", "t2d"), ("bmi", "stroke"), ("t2d", "stroke")]
P12 = ("p12_primary", "p12_sensitivity")


def mrow(region, anc, pair, row_class="primary", admissible="true", nc_set=""):
    a, b = pair
    return {"row_id": f"{region}__{anc}__{a}_vs_{b}", "ancestry": anc, "region_id": region, "region_safe": region,
            "trait_a": a, "trait_b": b, "row_class": row_class, "admissible": admissible,
            "inadmissible_reason": "" if admissible == "true" else "no_panel", "canonical_pair": "false",
            "nc_set": nc_set, "nc_caveat": ""}


def manifest(rows):
    return pd.DataFrame(rows, columns=MANIFEST_COLS).astype(str)


def doc(row_id, label, p12_key, h4, method=None, n_cs=(1, 1), anc="EUR", h3=None):
    """One coloc JSON as run_coloc_pair_r4.R writes it (pp_h4 == pp_h4_max, as the script writes for every method)."""
    if label.startswith("A1_"):
        arm, mode, method = f"A1_{anc}", label, f"A1_abf_{label.split('_', 1)[1]}"
        n_cs = (None, None)
    else:
        arm, mode, method = label, "susie", method or "coloc_susie"
    pp4 = h4
    rest = 1.0 - pp4
    pp3 = rest if h3 is None else h3
    pp0 = max(rest - pp3, 0.0)
    return {"row_id": row_id, "arm": arm, "mode": mode, "method": method, "p12_key": p12_key,
            "pp_h0": pp0, "pp_h1": 0.0, "pp_h2": 0.0, "pp_h3": pp3, "pp_h4": pp4, "pp_h4_max": h4,
            "n_cs_a": n_cs[0], "n_cs_b": n_cs[1],
            "fallback_reason": "n_cs_a==0" if method == "fallback_abf" else None}


def universe(n_regions=10, seed=7):
    """Every row class: EUR primary admissible (n_regions x 5 pairs), EUR primary inadmissible, EUR negative
    controls, AFR primary. Docs for every EUR/AFR production arm, A1 matched + allvars, a repro arm, both p12 keys.
    A2 and A1_matched sit above A3 by a region-specific shift on the confirmatory rows."""
    rnd = random.Random(seed)
    m, docs = [], []
    regions = [f"REG{i:02d}" for i in range(n_regions)]
    for reg in regions:
        for p in PAIRS:
            m.append(mrow(reg, "EUR", p))
    m.append(mrow("REGX", "EUR", PAIRS[0], admissible="false"))
    for nc in ("NC_ABO", "NC_NULL1"):
        for p in PAIRS[:3]:
            m.append(mrow(nc, "EUR", p, row_class="negative_control", nc_set="blood_group"))
    for p in PAIRS:
        m.append(mrow("AREG", "AFR", p))
    for r in m:
        if r["admissible"] != "true":
            continue
        rid, anc = r["row_id"], r["ancestry"]
        shift = 0.05 + 0.02 * (int(r["region_safe"][3:5]) if r["region_safe"][3:5].isdigit() else 0)
        for k in P12:
            base = round(rnd.uniform(0.2, 0.7), 4)
            shift += round(rnd.uniform(0, 0.01), 5)  # distinct per-row deltas
            if anc == "EUR":
                labels = {"A3_1kg": base, "A2_identity": min(base + shift, 0.99), "A1_matched": min(base + shift, 0.99),
                          "A1_allvars": round(rnd.uniform(0, 1), 4), "A3_ukb": round(rnd.uniform(0, 1), 4),
                          "A3_ukb_isect": round(rnd.uniform(0, 1), 4), "A3_1kg_isect": round(rnd.uniform(0, 1), 4),
                          "repro_routeC": round(rnd.uniform(0, 1), 4)}
            else:
                labels = {"AFR661_A3": base, "AFR661_A2": round(rnd.uniform(0, 1), 4),
                          "AFR504_A3": round(rnd.uniform(0, 1), 4), "A1_matched": round(rnd.uniform(0, 1), 4),
                          "A1_allvars": round(rnd.uniform(0, 1), 4)}
            for lab, h4 in labels.items():
                docs.append(doc(rid, lab, k, h4, anc=anc))
    return manifest(m), docs
