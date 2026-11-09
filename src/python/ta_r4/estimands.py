"""R4 estimands E1-E8 and the confirmatory contrast (D-26, D-02; Pitfalls 8 and 9).

Every selection rule, threshold and cut-off is read from config/ta_r4/decision_rules.yaml at call time.
Outputs are DRAFT unless the three lockable configs are locked, the W4a-T3 sign-off verifies and matches
them, and the offline lock gate passes for stage production (output_status).
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd
import yaml

from ta_r4 import paths
from ta_r4.signoff import SignoffError, canonical_sha256, verify_signoff

RULES_REL = "config/ta_r4/decision_rules.yaml"
MANIFEST_REL = "config/ta_r4/pair_manifest.tsv"
PRIORS_REL = "config/ta_r4/coloc_priors.yaml"
PP_COLS = ("pp_h0", "pp_h1", "pp_h2", "pp_h3", "pp_h4")
DOC_COLS = ("row_id", "arm", "mode", "method", "p12_key", *PP_COLS, "pp_h4_max", "n_cs_a", "n_cs_b",
            "fallback_reason", "none_reason", "n_snps")
EARLY_EXIT = ("no_variants", "too_many_variants")  # validate_r4_fits.EARLY_EXIT
NONE_REASONS = ("coloc_susie_empty", "coloc_susie_no_finite_h4", "fit_early_exit")  # run_coloc_pair_r4.R
PARTIAL_KEYS = ("ci_pos_mcnemar_ns", "ci_pos_mcnemar_opposite", "ci_neg_mcnemar_ns", "ci_neg_mcnemar_opposite")


# ------------------------------------------------------------------ inputs

def load_rules(path_or_repo) -> dict:
    p = Path(path_or_repo)
    if p.is_dir():
        p = p / RULES_REL
    return yaml.safe_load(p.read_text())


def load_manifest(repo) -> pd.DataFrame:
    return pd.read_csv(Path(repo) / MANIFEST_REL, sep="\t", dtype=str, keep_default_na=False)


def region_stat(row):
    """(region-level PP.H4, is_fallback): coloc_susie -> pp_h4_max over CS pairs; fallback_abf and A1 -> PP.H4;
    none (early exit / empty coloc.susie) -> (nan, False)."""
    method = row["method"]
    if method == "none":
        return float("nan"), False
    if method == "coloc_susie":
        return _num(row["pp_h4_max"]), False
    if method == "fallback_abf":
        return _num(row["pp_h4"]), True
    if isinstance(method, str) and method.startswith("A1_abf_"):
        return _num(row["pp_h4"]), False
    raise ValueError(f"unknown coloc method {method!r}")


def _num(v):
    return float("nan") if v is None or (isinstance(v, float) and math.isnan(v)) else float(v)


def build_rows(docs, manifest) -> pd.DataFrame:
    """Coloc JSON docs -> one row per output, joined to the pair manifest on row_id.
    label = the arm, or A1_matched / A1_allvars for A1 outputs (varset = matched / allvars)."""
    recs = []
    for d in docs:
        r = {k: d.get(k) for k in DOC_COLS}
        mode = d.get("mode")
        if isinstance(mode, str) and mode.startswith("A1_"):
            r["label"], r["varset"] = mode, mode.split("_", 1)[1]
        else:
            r["label"], r["varset"] = d.get("arm"), None
        r["region_stat"], r["is_fallback"] = region_stat(d)
        recs.append(r)
    rows = pd.DataFrame(recs, columns=[*DOC_COLS, "label", "varset", "region_stat", "is_fallback"])
    key = ["row_id", "label", "p12_key"]
    dup = rows.duplicated(key, keep=False)
    if dup.any():
        raise ValueError(f"duplicate coloc outputs for {rows.loc[dup, key].drop_duplicates().values.tolist()[:3]}")
    unknown = sorted(set(rows.row_id) - set(manifest.row_id))
    if unknown:
        raise ValueError(f"coloc outputs for row ids not in the pair manifest: {unknown[:3]}")
    man = manifest.drop(columns=[c for c in ("arm",) if c in manifest.columns])
    return rows.merge(man, on="row_id", how="left", validate="many_to_one")


def coloc_json_paths(repo):
    """Every coloc JSON under paths.result_dirs('coloc') (production arms + A1_EUR/A1_AFR) and nowhere else."""
    out = []
    for d in paths.result_dirs("coloc"):
        out += sorted((Path(repo) / d).glob("*.json"))
    return out


def load_rows(repo, manifest=None) -> pd.DataFrame:
    manifest = load_manifest(repo) if manifest is None else manifest
    docs = [json.loads(p.read_text()) for p in coloc_json_paths(repo)]
    return build_rows(docs, manifest)


def fit_frame(records) -> pd.DataFrame:
    """records: (arm, trait, ancestry, region_safe, fit JSON doc) -> one row per fit."""
    out = []
    for arm, trait, anc, reg, d in records:
        cs = d.get("credible_sets")
        sets = list(cs.values()) if isinstance(cs, dict) else []
        ok = d.get("status") in ("ok", "non_converged") and cs is not None
        d3 = d.get("d3_ld_quality") or {}
        out.append({"arm": arm, "trait": trait, "ancestry": anc, "region_safe": reg, "status": d.get("status"),
                    "n_cs": len(sets) if ok else pd.NA,
                    "cs_sizes": ";".join(str(len(s)) for s in sets) if ok else pd.NA,
                    "lambda_hat": _num(d.get("d3b_ld_z_consistency_s")),
                    "kriging_n_outliers": _num(d3.get("n_outliers")),
                    "kriging_max_logLR": _num(d3.get("max_logLR")),
                    "ld_allele_exact": _num(d.get("ld_allele_exact")),
                    "ld_allele_flipped": _num(d.get("ld_allele_flipped")),
                    "L_saturated": d.get("L_saturated"),
                    "min_abs_corr_sweep": d.get("min_abs_corr_sweep") or []})
    return pd.DataFrame(out, columns=["arm", "trait", "ancestry", "region_safe", "status", "n_cs", "cs_sizes",
                                      "lambda_hat", "kriging_n_outliers", "kriging_max_logLR", "ld_allele_exact",
                                      "ld_allele_flipped", "L_saturated", "min_abs_corr_sweep"])


def load_fits(repo) -> pd.DataFrame:
    """Fit JSONs under paths.result_dirs('fits'): {trait}.{ancestry}.{region_safe}.json."""
    recs = []
    for d in paths.result_dirs("fits"):
        arm = d.split("/")[-3]
        for p in sorted((Path(repo) / d).glob("*.json")):
            if p.name.endswith(".ld_receipt.json"):
                continue
            trait, anc, reg = p.name[: -len(".json")].split(".", 2)
            recs.append((arm, trait, anc, reg, json.loads(p.read_text())))
    return fit_frame(recs)


# ------------------------------------------------------------------ selection

def _match(col: pd.Series, want) -> pd.Series:
    vals = want if isinstance(want, (list, tuple)) else [want]
    norm = {str(v).lower() if isinstance(v, bool) else str(v) for v in vals}
    return col.astype(str).isin(norm)


def select_manifest(manifest, spec) -> pd.DataFrame:
    """Manifest rows matching every key of spec that is a manifest column."""
    keep = pd.Series(True, index=manifest.index)
    for k, v in spec.items():
        if k in manifest.columns:
            keep &= _match(manifest[k], v)
    return manifest[keep]


def confirmatory_rows(manifest, rules) -> pd.DataFrame:
    return select_manifest(manifest, rules["confirmatory"]["rows"])


def _side_rows(rows, label, row_ids, p12_key, a1_varset):
    s = rows[(rows.label == label) & rows.row_id.isin(row_ids) & (rows.p12_key == p12_key)]
    if label.startswith("A1_") and a1_varset is not None:
        s = s[s.varset == a1_varset]
    return s


def paired_frame(rows, X, ref, p12_key, both_rule, row_ids=None, a1_varset=None) -> pd.DataFrame:
    """X and ref outputs joined on (row_id, p12_key); delta = region_stat(X) - region_stat(ref)."""
    ids = set(rows.row_id) if row_ids is None else set(row_ids)
    cols = ["row_id", "method", "region_stat", "is_fallback", *PP_COLS, "n_snps"]
    x = _side_rows(rows, X, ids, p12_key, a1_varset)[cols]
    r = _side_rows(rows, ref, ids, p12_key, a1_varset)
    meta = r[["row_id", "region_safe", "ancestry", "row_class", "nc_set"]]
    p = x.add_prefix("x_").rename(columns={"x_row_id": "row_id"}).merge(
        r[cols].add_prefix("ref_").rename(columns={"ref_row_id": "row_id"}), on="row_id", how="inner")
    p = p.merge(meta, on="row_id", how="left")
    p.insert(1, "p12_key", p12_key)
    p.insert(1, "contrast", f"{X}_vs_{ref}")
    p = p.rename(columns={"x_region_stat": "x_stat", "ref_region_stat": "ref_stat"})
    p["delta"] = p.x_stat - p.ref_stat
    p["is_fallback"] = p.x_is_fallback.astype(bool) | p.ref_is_fallback.astype(bool)
    p["both_have_cs"] = _both_mask(p, X, ref, both_rule)
    return p.sort_values("row_id").reset_index(drop=True)


def _both_mask(p, X, ref, rule):
    """rule: "both methods <method>" or "<arm prefix> method <method>" (confirmatory.both_have_cs)."""
    toks = str(rule).split()
    if len(toks) != 3 or toks[1] not in ("method", "methods"):
        raise ValueError(f"both_have_cs rule {rule!r} is not '<who> method <method>'")
    who, method = toks[0], toks[2]
    if who == "both":
        return (p.x_method == method) & (p.ref_method == method)
    if ref.startswith(who):
        return p.ref_method == method
    if X.startswith(who):
        return p.x_method == method
    raise ValueError(f"both_have_cs rule {rule!r} names neither {X} nor {ref}")


def e1_paired_delta(rows, X, ref, p12_key, both_rule, row_ids=None, a1_varset=None) -> dict:
    """{'both_have_cs': paired rows where the CS rule holds, 'all_rows': every paired row (fallback labelled)}."""
    p = paired_frame(rows, X, ref, p12_key, both_rule, row_ids, a1_varset)
    p = p[p.x_stat.notna() & p.ref_stat.notna()]
    return {"both_have_cs": p[p.both_have_cs].reset_index(drop=True), "all_rows": p.reset_index(drop=True)}


# ------------------------------------------------------------------ statistics

def cluster_bootstrap_ci(values, clusters, B, seed, level=0.95, stat=np.median):
    """Percentile CI of stat(values), resampling whole clusters with replacement. NaN pair if < 2 values."""
    v = np.asarray(values, dtype=float)
    if v.size < 2:
        return (float("nan"), float("nan"))
    if np.isnan(v).any():
        raise ValueError("cluster_bootstrap_ci: NaN in values")
    nanstat = {np.median: np.nanmedian, np.mean: np.nanmean}.get(stat)
    if nanstat is None:
        raise ValueError("cluster_bootstrap_ci: stat must be np.median or np.mean")
    cl = np.asarray(clusters)
    groups = [v[cl == c] for c in sorted(set(cl.tolist()))]
    k = len(groups)
    pad = np.full((k, max(len(g) for g in groups)), np.nan)  # cluster x member, NaN-padded
    for i, g in enumerate(groups):
        pad[i, : len(g)] = g
    picks = np.random.default_rng(seed).integers(0, k, size=(B, k))
    stats = np.concatenate([nanstat(pad[picks[s: s + 1000]].reshape(len(picks[s: s + 1000]), -1), axis=1)
                            for s in range(0, B, 1000)])
    a = (1 - level) / 2
    lo, hi = np.percentile(stats, [100 * a, 100 * (1 - a)])
    return (float(lo), float(hi))


def _binom_two_sided(k, n):
    """Exact two-sided sign-test p for k successes of n at 0.5: 2 * P(X <= min(k, n-k)), capped at 1."""
    if n == 0:
        return 1.0
    m = min(k, n - k)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(m + 1)) / 2 ** n)


def sign_test(deltas) -> float:
    d = [x for x in deltas if not (isinstance(x, float) and math.isnan(x))]
    pos, neg = sum(1 for x in d if x > 0), sum(1 for x in d if x < 0)
    return _binom_two_sided(pos, pos + neg)


def mcnemar_exact(b, c):
    """(exact two-sided p, direction): b = X calls H4 and ref does not, c = the reverse."""
    b, c = int(b), int(c)
    direction = "X>A3" if b > c else ("A3>X" if c > b else "none")
    return _binom_two_sided(b, b + c), direction


def region_signflip(d_by_region, *, exact_max_k, B, seed) -> dict:
    """Two-sided region-level sign-flip test of T = sum of d_r (d_r = b_r - c_r, integers): p = share of sign
    assignments of the k regions with d_r != 0 with |T*| >= |T|; exact when k <= exact_max_k, else B seeded
    Monte Carlo draws with p = (1 + count) / (B + 1)."""
    d = np.array([int(v) for v in d_by_region.values() if int(v) != 0], dtype=np.int64)
    T, k = int(d.sum()), int(d.size)
    direction = "X>A3" if T > 0 else ("A3>X" if T < 0 else "none")
    hits = 0
    if k <= int(exact_max_k):
        bits = np.arange(k, dtype=np.int64)
        for s in range(0, 2 ** k, 1 << 16):
            idx = np.arange(s, min(s + (1 << 16), 2 ** k), dtype=np.int64)
            hits += int((np.abs((1 - 2 * ((idx[:, None] >> bits) & 1)) @ d) >= abs(T)).sum())
        p, method = hits / 2 ** k, "exact"
    else:
        B = int(B)
        rng = np.random.default_rng(int(seed))
        for s in range(0, B, 1000):
            signs = 1 - 2 * rng.integers(0, 2, size=(min(1000, B - s), k), dtype=np.int64)
            hits += int((np.abs(signs @ d) >= abs(T)).sum())
        p, method = (1 + hits) / (B + 1), "monte_carlo"
    return {"T": T, "k": k, "p": p, "method": method, "direction": direction}


def cohen_kappa(table) -> float:
    (a, b), (c, d) = table
    n = a + b + c + d
    if n == 0:
        return float("nan")
    po = (a + d) / n
    pe = ((a + b) * (a + c) + (c + d) * (b + d)) / n ** 2
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def _calls(p, thr):
    x, r = p.x_stat >= thr, p.ref_stat >= thr
    return int((x & r).sum()), int((x & ~r).sum()), int((~x & r).sum()), int((~x & ~r).sum())


def agreement(p, thr) -> dict:
    a, b, c, d = _calls(p, thr)
    n = a + b + c + d
    pval, direction = mcnemar_exact(b, c)
    return {"threshold": thr, "n": n, "a": a, "b": b, "c": c, "d": d, "kappa": cohen_kappa([[a, b], [c, d]]),
            "observed_agreement": (a + d) / n if n else float("nan"), "mcnemar_p": pval,
            "mcnemar_direction": direction}


def e2_agreement(p, thresholds) -> pd.DataFrame:
    return pd.DataFrame([agreement(p, t) for t in thresholds])


def e3_reclassification(p) -> pd.DataFrame:
    """Counts of (argmax hypothesis under X, argmax under ref) over H0..H4."""
    def cls(prefix):
        m = p[[f"{prefix}_{c}" for c in PP_COLS]].astype(float).to_numpy()
        return [f"H{int(np.argmax(r))}" if np.isfinite(r).all() else "NA" for r in m]
    t = pd.DataFrame({"class_x": cls("x"), "class_ref": cls("ref")})
    return t.value_counts().rename("n").reset_index().sort_values(["class_x", "class_ref"]).reset_index(drop=True)


def _no_cs(r):
    """Pair row with zero credible sets on either trait (n_cs NA, e.g. an early exit, is not counted)."""
    return (pd.to_numeric(r.n_cs_a) == 0) | (pd.to_numeric(r.n_cs_b) == 0)


def _fit_no_cs(f):
    """Fits with no credible set: zero sets, or an early exit (n_cs NA)."""
    return f.n_cs.isna() | (pd.to_numeric(f.n_cs) == 0)


def e4_no_cs_rate(rows, fits) -> pd.DataFrame:
    """No-CS rate at three levels, each with its denominator named: pair_row (rows with n_cs_a == 0 or n_cs_b == 0
    / pair rows of the arm), region (the same per region), fit (fits with zero sets or an early exit / fits of the
    arm). A1 has no fits and is excluded."""
    r = rows[~rows.label.astype(str).str.startswith("A1_")].copy()
    r["no_cs"] = _no_cs(r)
    out = []
    for level, by, den in (("pair_row", [], "pair rows of the arm"),
                           ("region", ["region_safe"], "pair rows of the arm in the region")):
        g = r.groupby(["ancestry", "row_class", "label", "p12_key", *by], dropna=False)
        t = g.agg(n_rows=("row_id", "size"), n_no_cs=("no_cs", "sum")).reset_index()
        out.append(t.assign(level=level, denominator=den))
    f = fits.assign(no_cs=_fit_no_cs(fits), early=fits.status.isin(EARLY_EXIT))
    t = f.groupby(["ancestry", "arm"]).agg(n_rows=("trait", "size"), n_no_cs=("no_cs", "sum"),
                                           n_early_exit=("early", "sum")).reset_index().rename(columns={"arm": "label"})
    out.append(t.assign(level="fit", denominator="fits of the arm"))
    cols = ["level", "denominator", "ancestry", "row_class", "label", "p12_key", "region_safe", "n_rows", "n_no_cs",
            "n_early_exit", "no_cs_rate"]
    t = pd.concat([x for x in out if len(x)], ignore_index=True) if any(len(x) for x in out) else pd.DataFrame(
        columns=cols)
    t = t.reindex(columns=cols)
    t["n_no_cs"] = t.n_no_cs.astype(int)
    t["no_cs_rate"] = t.n_no_cs / t.n_rows
    return t


def row_drop_table(rows, manifest, contrasts, p12_keys, a1_varset=None) -> pd.DataFrame:
    """Outcome states per (contrast, p12 key, side): manifest rows expected, outputs by method (none split by
    none_reason class), paired rows, both-have-CS rows and paired rows dropped from both_have_cs. contrasts:
    (X, ref, variant_set, both_rule). The counts must reconcile, else ValueError."""
    ids = set(manifest.row_id)
    out = []
    for X, ref, vset, rule in contrasts:
        for k in p12_keys:
            p = paired_frame(rows, X, ref, k, rule, ids, a1_varset)
            fin = p[p.x_stat.notna() & p.ref_stat.notna()]
            n_both = int(fin.both_have_cs.sum())
            for side, label in (("x", X), ("ref", ref)):
                s = _side_rows(rows, label, ids, k, a1_varset)
                meth = s.method.astype(str)
                a1 = meth.str.startswith("A1_abf_")
                unknown = sorted(set(meth[~a1 & ~meth.isin(["coloc_susie", "fallback_abf", "none"])]))
                if unknown:
                    raise ValueError(f"row_drop_table: unknown coloc method(s) {unknown} for {label}")
                none = s[meth == "none"]
                cls = none.none_reason.fillna("unspecified").astype(str).str.split(":", n=1).str[0]
                r = {"contrast": f"{X}_vs_{ref}", "variant_set": vset, "p12_key": k, "side": side, "label": label,
                     "n_expected": len(ids), "n_output": len(s), "n_coloc_susie": int((meth == "coloc_susie").sum()),
                     "n_a1": int(a1.sum()), "n_fallback": int((meth == "fallback_abf").sum()),
                     "n_method_none": len(none)}
                for c in sorted(set(NONE_REASONS) | set(cls)):
                    r[f"n_none_{c}"] = int((cls == c).sum())
                r.update({"n_paired": len(p), "n_paired_finite": len(fin), "n_both_have_cs": n_both,
                          "n_dropped_not_both_have_cs": len(fin) - n_both})
                out.append(r)
            _reconcile(out[-2:])
    lead = ["contrast", "variant_set", "p12_key", "side", "label", "n_expected", "n_output", "n_coloc_susie", "n_a1",
            "n_fallback", "n_method_none"]
    t = pd.DataFrame(out)
    if not len(t):
        return pd.DataFrame(columns=lead)
    rest = [c for c in t.columns if c not in lead]
    return t[lead + rest].fillna({c: 0 for c in rest if c.startswith("n_none_")}).astype(
        {c: int for c in rest if c.startswith("n_none_")})


def _reconcile(pair):
    for r in pair:
        parts = r["n_coloc_susie"] + r["n_a1"] + r["n_fallback"] + r["n_method_none"]
        none = sum(v for c, v in r.items() if c.startswith("n_none_"))
        ok = (parts == r["n_output"] and none == r["n_method_none"] and r["n_output"] <= r["n_expected"]
              and r["n_both_have_cs"] <= r["n_paired_finite"] <= r["n_paired"])
        if not ok:
            raise ValueError(f"row_drop_table: counts do not reconcile: {r}")
    if pair[0]["n_paired"] > min(r["n_output"] for r in pair):
        raise ValueError(f"row_drop_table: n_paired exceeds an output count: {pair}")


def e4_finemap_structure(fits) -> pd.DataFrame:
    return fits[["arm", "trait", "ancestry", "region_safe", "status", "n_cs", "cs_sizes", "L_saturated"]].copy()


def e5_diagnostics(fits) -> pd.DataFrame:
    """estimate_s_rss lambda-hat (continuous; no cut-off) and kriging_rss outlier counts per fit."""
    return fits[["arm", "trait", "ancestry", "region_safe", "status", "lambda_hat", "kriging_n_outliers",
                 "kriging_max_logLR"]].copy()


def min_abs_corr_sweep(fits) -> pd.DataFrame:
    out = []
    for f in fits.itertuples():
        for s in f.min_abs_corr_sweep:
            out.append({"arm": f.arm, "trait": f.trait, "ancestry": f.ancestry, "region_safe": f.region_safe,
                        "min_abs_corr": s.get("min_abs_corr"), "n_cs": s.get("n_CS"),
                        "cs_sizes": ";".join(str(x) for x in (s.get("cs_sizes") or []))})
    return pd.DataFrame(out, columns=["arm", "trait", "ancestry", "region_safe", "min_abs_corr", "n_cs", "cs_sizes"])


def _share(flipped, exact):
    tot = flipped + exact
    return flipped / tot if tot > 0 else float("nan")


def e7_frozen_vs_fixed(known_w3a, known_sh2b3, fits, rows, qtl_docs, *, a3_arm, p12_key,
                       qtl_tiers_frozen=None, qtl_tiers_fixed=None) -> pd.DataFrame:
    """E-2 frozen (reproduction) vs fixed (R4 A3) table. Sections: fit_yield (W3a Route L real-LD fits),
    sh2b3_pair (W3b R2_exact pairs), flipped_share_region (fine-map, per region), flipped_share_qtl (per QTL row),
    qtl_tier (QTL_legacy vs QTL_A3 tiers). flipped_share = flipped / (exact + flipped)."""
    out = []

    def add(section, id_, region="", anc="", frozen="", fixed="", n_exact=float("nan"), n_flipped=float("nan"),
            share=float("nan")):
        out.append({"section": section, "id": id_, "region_safe": region, "ancestry": anc,
                    "frozen_value": frozen, "fixed_value": fixed, "changed": (frozen != fixed) if fixed != "" else pd.NA,
                    "n_exact": n_exact, "n_flipped": n_flipped, "flipped_share": share})

    fi = {(f.arm, f.trait, f.ancestry, f.region_safe): f for f in fits.itertuples()}
    for r in known_w3a[known_w3a["pair"] == "real_ld"].itertuples():
        f = fi.get((a3_arm.get(r.ancestry), r.trait, r.ancestry, r.region_safe))
        fixed = "absent" if f is None else f"{f.status};n_cs={'NA' if pd.isna(f.n_cs) else int(f.n_cs)}"
        add("fit_yield", f"{r.trait}.{r.ancestry}.{r.region_safe}", r.region_safe, r.ancestry,
            f"{r.status_L};n_cs={r.n_cs_L}", fixed)
    ri = {(r.row_id, r.label): r for r in rows[rows.p12_key == p12_key].itertuples()}
    for r in known_sh2b3[known_sh2b3["config_label"] == "R2_exact"].itertuples():
        anc = r.pair_id.split("__")[1]
        frozen = r.pp_h4_reproduced if str(r.pp_h4_reproduced) not in ("", "NA", "nan") else r.status
        x = ri.get((r.pair_id, a3_arm.get(anc)))
        add("sh2b3_pair", r.pair_id, r.pair_id.split("__")[0], anc, str(frozen),
            "absent" if x is None else repr(float(x.region_stat)))
    a3 = fits[fits.arm.isin(set(a3_arm.values()))]
    for (reg, anc), g in a3.groupby(["region_safe", "ancestry"]):
        e, fl = g.ld_allele_exact.fillna(0).sum(), g.ld_allele_flipped.fillna(0).sum()
        add("flipped_share_region", reg, reg, anc, n_exact=e, n_flipped=fl, share=_share(fl, e))
    for q in qtl_docs:
        e, fl = _num(q.get("qtl_orient_exact")), _num(q.get("qtl_orient_flipped"))
        share = _share(fl, e) if not (math.isnan(e) or math.isnan(fl)) else float("nan")
        add("flipped_share_qtl", q["id"], n_exact=e, n_flipped=fl, share=share)
    if qtl_tiers_frozen is not None and qtl_tiers_fixed is not None:
        fx = {(r.region, r.ancestry): r.tier for r in qtl_tiers_fixed.itertuples()}
        for r in qtl_tiers_frozen.itertuples():
            add("qtl_tier", f"{r.region}.{r.ancestry}", r.region, r.ancestry, str(r.tier),
                str(fx.get((r.region, r.ancestry), "absent")))
    return pd.DataFrame(out, columns=["section", "id", "region_safe", "ancestry", "frozen_value", "fixed_value",
                                      "changed", "n_exact", "n_flipped", "flipped_share"])


def wilson_ci(k, n, level=0.95):
    if n == 0:
        return (float("nan"), float("nan"))
    z = NormalDist().inv_cdf(1 - (1 - level) / 2)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def e8_simulation_rates(sim, threshold, level=0.95) -> pd.DataFrame:
    """Share of reps with region PP.H4 >= threshold per (arm, scenario, gen_panel), pooled over regions:
    false_H4 under H0/H3 truth, true_H4 under H4 truth; Wilson CI."""
    s = sim.copy()
    s["stat"] = [region_stat(r)[0] for r in s.to_dict("records")]
    out = []
    for (arm, sc, gp), g in s.groupby(["arm", "scenario", "gen_panel"]):
        n, k = int(g.stat.notna().sum()), int((g.stat >= threshold).sum())
        lo, hi = wilson_ci(k, n, level)
        m = re.match(r"^H3_r2_(.+)$", sc)
        out.append({"arm": arm, "scenario": sc, "gen_panel": gp, "r2_bin": m.group(1) if m else "",
                    "quantity": "true_H4" if sc == "H4" else "false_H4", "threshold": threshold, "n": n, "k": k,
                    "rate": k / n if n else float("nan"), "ci_lo": lo, "ci_hi": hi})
    return pd.DataFrame(out, columns=["arm", "scenario", "gen_panel", "r2_bin", "quantity", "threshold", "n", "k",
                                      "rate", "ci_lo", "ci_hi"])


# ------------------------------------------------------------------ the contrast

def describe_contrast(rows, X, ref, rules, row_ids, p12_key, both_rule, a1_varset=None, threshold=None) -> dict:
    """Paired statistics on the both-have-CS subset (no categories): CI, row-level McNemar (descriptive), kappa and
    the region-level sign-flip test on d_r = b_r - c_r per region."""
    e1 = e1_paired_delta(rows, X, ref, p12_key, both_rule, row_ids, a1_varset)
    sub = e1["both_have_cs"]
    d = sub.delta.to_numpy(dtype=float)
    lo, hi = cluster_bootstrap_ci(d, sub.region_safe.to_numpy(), B=int(rules["bootstrap_B"]),
                                  seed=int(rules["bootstrap_seed"]), level=float(rules["ci_level"]))
    thr = float(rules["threshold_primary"] if threshold is None else threshold)
    ag = agreement(sub, thr)
    x, r = sub.x_stat >= thr, sub.ref_stat >= thr
    d_r = ((x & ~r).astype(int) - (~x & r).astype(int)).groupby(sub.region_safe).sum()
    sf = region_signflip(d_r.to_dict(), exact_max_k=rules["confirmatory"]["region_signflip"]["exact_max_k"],
                         B=int(rules["bootstrap_B"]), seed=int(rules["bootstrap_seed"]))
    return {"contrast": f"{X}_vs_{ref}", "x": X, "ref": ref, "p12_key": p12_key,
            "n_rows": int(len(e1["all_rows"])), "n_both": int(len(sub)), "n_regions": int(sub.region_safe.nunique()),
            "median_delta": float(np.median(d)) if d.size else float("nan"),
            "mean_delta": float(np.mean(d)) if d.size else float("nan"),
            "ci_lo": lo, "ci_hi": hi, "sign_p": sign_test(d.tolist()),
            "mcnemar_b": ag["b"], "mcnemar_c": ag["c"], "mcnemar_p": ag["mcnemar_p"],
            "kappa": ag["kappa"], "observed_agreement": ag["observed_agreement"],
            "signflip_T": sf["T"], "signflip_k": sf["k"], "signflip_p": sf["p"], "signflip_method": sf["method"],
            "signflip_direction": sf["direction"]}


def e1_summary(sub, rules) -> dict:
    """Median and mean delta with region-cluster bootstrap CIs, fallback count and sign test for one subset."""
    d = sub.delta.to_numpy(dtype=float)
    cl = sub.region_safe.to_numpy()
    kw = {"B": int(rules["bootstrap_B"]), "seed": int(rules["bootstrap_seed"]), "level": float(rules["ci_level"])}
    mlo, mhi = cluster_bootstrap_ci(d, cl, **kw)
    alo, ahi = cluster_bootstrap_ci(d, cl, stat=np.mean, **kw)
    nan = float("nan")
    return {"n": int(d.size), "n_fallback": int(sub.is_fallback.sum()),
            "median_delta": float(np.median(d)) if d.size else nan, "median_ci_lo": mlo, "median_ci_hi": mhi,
            "mean_delta": float(np.mean(d)) if d.size else nan, "mean_ci_lo": alo, "mean_ci_hi": ahi,
            "sign_p": sign_test(d.tolist())}


def e6_panel_contrast(rows, fits, rules, row_ids, contrasts, p12_keys) -> pd.DataFrame:
    """contrasts: (X, ref, variant_set, both_rule). Long table of E1-E5 and drops per contrast and p12 key, from the
    same estimators as the primary contrasts: E1 (e1_summary, median variant counts), E2 (e2_agreement over the sweep)
    and E3 (e3_reclassification) on both_have_cs and all_rows; E4 no-CS rates (pair rows and fits) and E5
    (e5_diagnostics medians) per side; drops (row_drop_table)."""
    out = []
    ids = set(row_ids)
    regions = set(rows.loc[rows.row_id.isin(ids), "region_safe"])
    for X, ref, vset, rule in contrasts:
        for k in p12_keys:
            def add(est, subset, metric, value):
                out.append({"variant_set": vset, "contrast": f"{X}_vs_{ref}", "p12_key": k, "estimand": est,
                            "subset": subset, "metric": metric, "value": float(value)})

            for sname, df in e1_paired_delta(rows, X, ref, k, rule, ids).items():
                for m, v in e1_summary(df, rules).items():
                    add("E1", sname, m, v)
                for side in ("x", "ref"):
                    add("E1", sname, f"median_n_snps_{side}", pd.to_numeric(df[f"{side}_n_snps"]).median())
                add("E1", sname, "median_n_snps_diff",
                    (pd.to_numeric(df.x_n_snps) - pd.to_numeric(df.ref_n_snps)).median())
                for a in e2_agreement(df, rules["sweep"]).to_dict("records"):
                    for m in ("n", "a", "b", "c", "d", "kappa", "observed_agreement", "mcnemar_p"):
                        add("E2", sname, f"{m}@{a['threshold']}", a[m])
                for e in e3_reclassification(df).itertuples():
                    add("E3", sname, f"{e.class_x}->{e.class_ref}", e.n)
            for side, label in (("x", X), ("ref", ref)):
                s = _side_rows(rows, label, ids, k, None)
                add("E4", "-", f"{side}.pair_row.n_rows", len(s))
                add("E4", "-", f"{side}.pair_row.n_no_cs", int(_no_cs(s).sum()))
                if label.startswith("A1_"):
                    continue
                anc = set(s.ancestry) or set(rows.loc[rows.row_id.isin(ids), "ancestry"])
                f = fits[(fits.arm == label) & fits.region_safe.isin(regions) & fits.ancestry.isin(anc)]
                add("E4", "-", f"{side}.fit.n_rows", len(f))
                add("E4", "-", f"{side}.fit.n_no_cs", int(_fit_no_cs(f).sum()))
                d = e5_diagnostics(f)
                add("E5", "-", f"{side}.n_fits", len(d))
                add("E5", "-", f"{side}.median_lambda_hat", pd.to_numeric(d.lambda_hat).median())
                add("E5", "-", f"{side}.median_kriging_n_outliers", pd.to_numeric(d.kriging_n_outliers).median())
            drops = row_drop_table(rows, pd.DataFrame({"row_id": sorted(ids)}), [(X, ref, vset, rule)], [k])
            for r in drops.to_dict("records"):
                for m, v in r.items():
                    if m.startswith("n_"):
                        add("drops", "-", f"{r['side']}.{m}", v)
    return pd.DataFrame(out, columns=["variant_set", "contrast", "p12_key", "estimand", "subset", "metric", "value"])


def negative_control_rates(rows, threshold) -> pd.DataFrame:
    """Pre-specified specificity analysis: share of negative-control rows with region PP.H4 >= threshold."""
    nc = rows[rows.row_class == "negative_control"].copy()
    nc["h4"] = nc.region_stat >= threshold
    t = nc.groupby(["nc_set", "label", "p12_key"]).agg(n_rows=("row_id", "size"), n_h4=("h4", "sum")).reset_index()
    t["n_h4"] = t.n_h4.astype(int)
    t["share_h4"] = t.n_h4 / t.n_rows
    t.insert(3, "threshold", threshold)
    return t


def categorize(stats, rules) -> dict:
    """decision_rules.yaml confirmatory.categories, with alpha / kappa_cut / n_both_min from the top level and
    n_regions_min from confirmatory. The direction category is the region sign-flip test, not row-level McNemar."""
    lo, hi = stats["ci_lo"], stats["ci_hi"]
    ci = "incl0"
    if not (math.isnan(lo) or math.isnan(hi)):
        ci = "pos" if lo > 0 else ("neg" if hi < 0 else "incl0")
    p, T = stats["signflip_p"], stats["signflip_T"]
    alpha = float(rules["alpha"])
    mcn = "sig_X_gt_A3" if (p < alpha and T > 0) else ("sig_A3_gt_X" if (p < alpha and T < 0) else "ns")
    k, po = stats["kappa"], stats["observed_agreement"]
    kappa_ok = bool(po == 1) if math.isnan(k) else bool(k >= float(rules["kappa_cut"]))
    n_both_ok = (stats["n_both"] >= int(rules["n_both_min"])
                 and stats["n_regions"] >= int(rules["confirmatory"]["n_regions_min"]))
    return {"n_both_ok": bool(n_both_ok), "ci": ci, "mcnemar": mcn, "kappa_ok": kappa_ok}


class ConfirmatoryIncomplete(ValueError):
    """The observed outputs do not hold exactly one output per confirmatory manifest row on each side."""


def _check_complete(rows, name, sides, ids, p12_key, a1_varset):
    bad = []
    for side in sides:
        n = _side_rows(rows, side, ids, p12_key, a1_varset).row_id.value_counts()
        missing, dup = sorted(set(ids) - set(n.index)), sorted(n.index[n > 1])
        if missing or dup:
            bad.append(f"{side}: {len(missing)} of {len(ids)} missing {missing[:5]}"
                       + (f", {len(dup)} duplicated {dup[:5]}" if dup else ""))
    if bad:
        raise ConfirmatoryIncomplete(f"{name} ({p12_key}): confirmatory outputs incomplete: " + "; ".join(bad))


def contrast_stats(rows, X, ref, rules, manifest) -> dict:
    """The confirmatory contrast X vs ref on the rows of rules['confirmatory']['rows'] only. The expected rows come
    from the pair manifest; any missing (or duplicated) output on either side raises ConfirmatoryIncomplete."""
    conf = rules["confirmatory"]
    name = f"{X}_vs_{ref}"
    if ref != conf["reference_arm"] or name not in conf["contrasts"]:
        raise ValueError(f"{name} is not a confirmatory contrast {conf['contrasts']} (reference {conf['reference_arm']})")
    if conf["ci"]["statistic"] != "median_delta_pph4":
        raise ValueError(f"unsupported CI statistic {conf['ci']['statistic']!r}")
    call = conf["mcnemar_kappa"]["call"].split(">=")
    thr = rules[call[1].strip()]
    sf = conf["region_signflip"]
    if sf["subset"] != "both_have_cs" or sf["call"] != conf["mcnemar_kappa"]["call"]:
        raise ValueError(f"region_signflip must use the both_have_cs subset and the mcnemar_kappa call: {sf}")
    spec = conf["rows"]
    ids = set(select_manifest(manifest, {k: v for k, v in spec.items() if k not in ("p12_key", "a1_varset")}).row_id)
    _check_complete(rows, name, (X, ref), ids, spec["p12_key"], spec.get("a1_varset"))
    s = describe_contrast(rows, X, ref, rules, ids, spec["p12_key"], conf["both_have_cs"][name],
                          a1_varset=spec.get("a1_varset"), threshold=thr)
    s["categories"] = categorize(s, rules)
    return s


# ------------------------------------------------------------------ FINAL / DRAFT

def _same(a, b):
    try:
        return float(a) == float(b)
    except (TypeError, ValueError):
        return str(a) == str(b)


def output_status(repo) -> str:
    """FINAL only if coloc_priors / decision_rules / simulation are locked: true, the W4a-T3 sign-off verifies and
    equals the locked values, and the offline lock gate passes for stage production. Otherwise DRAFT."""
    from ta_r4 import r4_lock_gate as gate

    repo = Path(repo)
    cfg = {}
    for n in gate.LOCKABLE:
        p = repo / f"config/ta_r4/{n}.yaml"
        if not p.exists():
            return "DRAFT"
        cfg[n] = yaml.safe_load(p.read_text()) or {}
        if cfg[n].get("locked") is not True:
            return "DRAFT"
    try:
        f = verify_signoff("W4a-T3", signoff_dir=repo / gate.SIGNOFF_REL)
    except SignoffError:
        return "DRAFT"
    dr, pri = cfg["decision_rules"], cfg["coloc_priors"]
    want = {"p12_primary": pri.get("p12_primary"), "kappa_cut": dr.get("kappa_cut"),
            "n_both_min": dr.get("n_both_min"),
            **{f"partial_rule.{k}": (dr.get("partial_rule") or {}).get(k) for k in PARTIAL_KEYS}}
    if any(not _same(v, f[k]) for k, v in want.items()):
        return "DRAFT"
    if "confirmatory" not in dr or canonical_sha256(dr["confirmatory"]) != f["confirmatory_sha256"]:
        return "DRAFT"
    gate._clear_cache()  # the gate caches per HEAD; a working-tree change must be re-checked
    try:
        gate.check_lock_gate(repo, "production")
    except gate.LockGateError:
        return "DRAFT"
    return "FINAL"


def with_status(obj, status):
    if status not in ("FINAL", "DRAFT"):
        raise ValueError(status)
    if isinstance(obj, pd.DataFrame):
        obj = obj.copy()
        obj.attrs["status"] = status
        return obj
    return dict(obj, status=status)
