"""The single entry point for every R4 table (W7 runs it; written and frozen in W3d).

Reads trait-pair coloc JSONs only from paths.result_dirs('coloc') and fits only from result_dirs('fits'); the E7
frozen side comes from the committed known-answer tables and the QTL_legacy tier table by explicit path. Every
statistic comes from estimands / branch_classifier. Exits 2 and writes nothing unless estimands.output_status
is FINAL; exits 3 and writes nothing if FINAL and coloc_coverage finds a missing or extra output (EUR or AFR) or a
QTL arm's summary or tier table is missing; exits 3 (FINAL and DRAFT) unless every simulation.yaml cell is present
with the configured replicate count;
--draft (fixtures only) writes every table labelled DRAFT. Every table carries a coverage header line.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd
import yaml

from ta_r4 import branch_classifier, coloc_coverage, estimands, paths
from ta_r4.arms import ARMS
from ta_r4.commands import A1_FIT_ARMS, P12_KEYS

TABLES = ("branch_outcomes", "e1_paired_delta", "e2_agreement_sweep", "e3_reclassification", "e4_finemap_structure",
          "e4_no_cs_rate", "e4_cross_purity", "e5_diagnostics", "e6_panel_contrast", "e7_frozen_vs_fixed",
          "e8_simulation_rates", "afr_secondary", "negative_controls", "qtl_layer", "min_abs_corr_sweep",
          "hla_exploratory", "table1_data", "row_drops", "qtl_rows")
KNOWN_W3A = f"{paths.MAN}/known_answer_W3a.tsv"
KNOWN_SH2B3 = f"{paths.MAN}/known_answer_sh2b3.tsv"
SIM_DIR = f"{paths.R4}/results/sim"
SIM_CFG = "config/ta_r4/simulation.yaml"
SIM_ARMS = ("A1", "A2", "A3")
QTL_ARMS = ("QTL_A3", "QTL_A2", "QTL_legacy")
QTL_TIERS = f"{paths.R4}/results/{{arm}}/qtl_tiers.tsv"
QTL_SUMMARY = f"{paths.R4}/results/{{arm}}/qtl_coloc_summary.tsv"  # aggregate_qtl_coloc --with-method-columns
QTL_JSON_DIR = f"{paths.R4}/results/QTL_A3/qtl"
TIER_COLS = ["region", "ancestry", "tier", "best_gwas_pph4", "best_qtl_pph4", "resolving_gene", "resolving_tissue",
             "resolving_qtl_source", "all_supporting_sources", "neg_ctrl_set"]
RSCRIPT = "Rscript"  # from envs/r_coloc.yml on PATH (as commands.py)
CROSS_PURITY_R = "src/snakemake/scripts/ta_r4/cs_cross_purity.R"
#: (fit arm, panel arm, allow absent members) scored by cs_cross_purity.R (Pitfall 9). Absent members are allowed
#: only between panels with different variant sets (native UKB/1000G, AFR504/AFR661).
CROSS_PURITY = (("A2_identity", "A3_1kg", False), ("A3_ukb", "A3_1kg", True), ("A3_1kg", "A3_ukb", True),
                ("A3_ukb_isect", "A3_1kg_isect", False), ("A3_1kg_isect", "A3_ukb_isect", False),
                ("AFR661_A2", "AFR661_A3", False), ("AFR504_A3", "AFR661_A3", True), ("AFR661_A3", "AFR504_A3", True))
#: descriptive contrasts (never classified): (X, ref, variant_set, both_have_cs rule)
E6 = (("A3_ukb", "A3_1kg", "native", "both methods coloc_susie"),
      ("A3_ukb_isect", "A3_1kg_isect", "isect", "both methods coloc_susie"))
AFR = (("AFR661_A2", "AFR661_A3", "matched", "both methods coloc_susie"),
       ("A1_matched", "AFR661_A3", "matched", "AFR661_A3 method coloc_susie"),
       ("AFR504_A3", "AFR661_A3", "matched", "both methods coloc_susie"))
HLA = ("A3_ukb", "HLA_6p21")
HLA_NOTE = "exploratory A3_ukb fit; no coloc row: no admissible comparator panel (D-24)"
PURITY_COLS = ["fit_arm", "panel_arm", "fit_status", "trait", "ancestry", "region_safe", "cs", "size",
               "n_cs_variants", "n_present", "min_abs_corr", "mean_abs_corr", "purity_fit", "note"]


def _rscript_purity(repo, fit_rds, panel_rds, allow_absent):
    tmp = Path(repo) / paths.R4 / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=tmp) as td:
        out = Path(td) / "cross_purity.tsv"
        subprocess.run([RSCRIPT, str(Path(repo) / CROSS_PURITY_R), "--fit", str(fit_rds), "--panel", str(panel_rds),
                        "--output", str(out), *(["--allow-absent"] if allow_absent else [])],
                       check=True, capture_output=True, text=True)
        return pd.read_csv(out, sep="\t", keep_default_na=False, na_values=["NA"])


def _cross_purity(repo, fits, runner):
    """Every fit of each fit arm, whatever its status. Fits that exited early, have no RDS / panel, or whose RDS has
    no credible set get one row with a note; a fit with sets gets one row per set."""
    out = []
    for fit_arm, panel_arm, allow_absent in CROSS_PURITY:
        for f in fits[fits.arm == fit_arm].itertuples():
            key = {"fit_arm": fit_arm, "panel_arm": panel_arm, "fit_status": f.status, "trait": f.trait,
                   "ancestry": f.ancestry, "region_safe": f.region_safe}
            if f.status in estimands.EARLY_EXIT:
                out.append({**key, "note": "early_exit"})
                continue
            rds = Path(repo) / paths.fit_rds(fit_arm, f.trait, f.ancestry, f.region_safe)
            panel = Path(repo) / paths.panel_path(panel_arm, f.region_safe)
            if not rds.exists() or not panel.exists():
                out.append({**key, "note": "fit_rds_missing" if not rds.exists() else "panel_missing"})
                continue
            t = runner(repo, rds, panel, allow_absent)
            if not len(t):
                out.append({**key, "note": "no_cs"})
            out += [{**key, **r} for r in t.to_dict("records")]
    return pd.DataFrame(out, columns=PURITY_COLS)


def _read_tsv(p):
    return pd.read_csv(p, sep="\t", comment="#", dtype=str, keep_default_na=False)


def expected_sim_cells(repo):
    """({file name: (region, scenario, gen_panel)}, reps) for every cell of the repo's config/ta_r4/simulation.yaml."""
    cfg = yaml.safe_load((Path(repo) / SIM_CFG).read_text())
    cells = {f"{r}.{s}.{g}.tsv": (r, s, g) for r in cfg["regions"] for s in cfg["scenarios"] for g in cfg["gen_panels"]}
    return cells, int(cfg["reps"])


def _sim(repo, *, final):
    """Every expected cell file, read and checked: status ok with reps rows per arm (A1, A2, A3) and, in FINAL,
    reps_override=none; or status no_qualifying_pair with 0 rows. A missing, extra or failing file raises
    SimulationIncomplete."""
    cells, reps = expected_sim_cells(repo)
    files = {p.name: p for p in (Path(repo) / SIM_DIR).glob("*.tsv")}
    bad = [f"missing {n}" for n in sorted(set(cells) - set(files))]
    bad += [f"extra {n}" for n in sorted(set(files) - set(cells))]
    frames, meta = [], []
    for name in sorted(set(cells) & set(files)):
        p = files[name]
        head = dict(ln[2:].split("=", 1) for ln in p.read_text().splitlines() if ln.startswith("# ") and "=" in ln
                    and " " not in ln[2:].split("=", 1)[0])
        status, override = head.get("status", ""), head.get("reps_override", "")
        df = pd.read_csv(p, sep="\t", comment="#")
        if status == "ok":
            n_arm = df.arm.value_counts().to_dict() if len(df) else {}
            if n_arm != {a: reps for a in SIM_ARMS}:
                bad.append(f"{name}: rows per arm {n_arm} != {reps} x {SIM_ARMS}")
            if final and override != "none":
                bad.append(f"{name}: reps_override={override!r} (FINAL requires none)")
        elif status == "no_qualifying_pair":
            if len(df):
                bad.append(f"{name}: status no_qualifying_pair with {len(df)} rows")
        else:
            bad.append(f"{name}: status {status!r}")
        r, sc, g = cells[name]
        meta.append({"scenario": sc, "gen_panel": g, "no_qualifying_pair": status == "no_qualifying_pair"})
        frames.append(df)
    if bad:
        raise estimands.SimulationIncomplete(f"simulation incomplete: {len(bad)} problem(s) over {len(cells)} cells: "
                                             + "; ".join(bad[:10]))
    sim = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return sim, pd.DataFrame(meta, columns=["scenario", "gen_panel", "no_qualifying_pair"])


def _e8(repo, rules, *, final):
    sim, meta = _sim(repo, final=final)
    cols = ["arm", "scenario", "gen_panel", "region", "method", "pp_h4", "pp_h4_max"]
    sim = sim if len(sim) else pd.DataFrame(columns=cols)
    t = estimands.e8_simulation_rates(sim, float(rules["threshold_primary"]), float(rules["ci_level"]))
    files = meta.groupby(["scenario", "gen_panel"]).agg(
        n_files=("no_qualifying_pair", "size"), n_files_no_qualifying_pair=("no_qualifying_pair", "sum")).reset_index()
    t = t.merge(files, on=["scenario", "gen_panel"], how="outer")
    t["n"] = t.n.fillna(0).astype(int)
    t["k"] = t.k.fillna(0).astype(int)
    for c in ("n_files", "n_files_no_qualifying_pair"):
        t[c] = t[c].fillna(0).astype(int)
    return t


def _qtl(repo):
    tiers = {}
    for arm in QTL_ARMS:
        p = Path(repo) / QTL_TIERS.format(arm=arm)
        if p.exists():
            tiers[arm] = _read_tsv(p)
    layer = [t.assign(qtl_arm=a) for a, t in tiers.items()]
    layer = pd.concat(layer, ignore_index=True) if layer else pd.DataFrame(columns=TIER_COLS + ["qtl_arm"])
    layer = layer[["qtl_arm", *[c for c in layer.columns if c != "qtl_arm"]]]
    docs = []
    qdir = Path(repo) / QTL_JSON_DIR
    for p in sorted(qdir.rglob("*.json")) if qdir.is_dir() else []:
        docs.append({"id": str(p.relative_to(qdir))[: -len(".json")], **json.loads(p.read_text())})
    return layer, docs, tiers.get("QTL_legacy"), tiers.get("QTL_A3")


def _qtl_rows(repo):
    """Every row of each QTL arm's qtl_coloc_summary.tsv (coloc_susie, fallback_abf and none), with qtl_arm."""
    t = [_read_tsv(p).assign(qtl_arm=a) for a in QTL_ARMS
         for p in [Path(repo) / QTL_SUMMARY.format(arm=a)] if p.exists()]
    t = pd.concat(t, ignore_index=True) if t else pd.DataFrame(columns=["qtl_coloc_id"]).assign(qtl_arm=None)
    return t[["qtl_arm", *[c for c in t.columns if c != "qtl_arm"]]]


def _qtl_missing(repo):
    return [p for a in QTL_ARMS for p in (QTL_SUMMARY.format(arm=a), QTL_TIERS.format(arm=a))
            if not (Path(repo) / p).exists()]


def _ids(man, rules, **override):
    spec = {k: v for k, v in rules["confirmatory"]["rows"].items() if k not in ("p12_key", "a1_varset")}
    return set(estimands.select_manifest(man, {**spec, **override}).row_id)


def build_tables(repo, rules, man, rows, fits, purity_runner, *, final):
    conf = rules["confirmatory"]
    ref = conf["reference_arm"]
    a1v = conf["rows"].get("a1_varset")
    ids = _ids(man, rules)
    t = {}

    bo = []
    for name in conf["contrasts"]:
        x, r = name.split("_vs_")
        s = estimands.contrast_stats(rows, x, r, rules, man)
        branch, via = branch_classifier.classify(s, rules)
        cat = s.pop("categories")
        bo.append({**s, **cat, "branch": branch, "via": via})
    t["branch_outcomes"] = pd.DataFrame(bo)

    e1, e2, e3 = [], [], []
    for name in conf["contrasts"]:
        x = name.split("_vs_")[0]
        for k in P12_KEYS:
            sub = estimands.e1_paired_delta(rows, x, ref, k, conf["both_have_cs"][name], ids, a1v)
            keep = ["row_id", "region_safe", "x_method", "ref_method", "x_stat", "ref_stat", "delta", "is_fallback",
                    "both_have_cs"]
            e1.append(sub["all_rows"][keep].assign(level="row", contrast=name, p12_key=k))
            for sname, df in sub.items():
                e1.append(pd.DataFrame([{"level": "summary", "contrast": name, "p12_key": k, "subset": sname,
                                         **estimands.e1_summary(df, rules)}]))
                e2.append(estimands.e2_agreement(df, rules["sweep"]).assign(contrast=name, p12_key=k, subset=sname))
                e3.append(estimands.e3_reclassification(df).assign(contrast=name, p12_key=k, subset=sname))
    lead = ["level", "contrast", "p12_key", "subset"]
    e1 = pd.concat(e1, ignore_index=True)
    t["e1_paired_delta"] = e1[lead + [c for c in e1.columns if c not in lead]]
    lead = ["contrast", "p12_key", "subset"]
    for key, parts in (("e2_agreement_sweep", e2), ("e3_reclassification", e3)):
        df = pd.concat(parts, ignore_index=True)
        t[key] = df[lead + [c for c in df.columns if c not in lead]]

    t["e4_finemap_structure"] = estimands.e4_finemap_structure(fits)
    t["e4_no_cs_rate"] = estimands.e4_no_cs_rate(rows, fits)
    t["e4_cross_purity"] = _cross_purity(repo, fits, purity_runner)
    real_ld = [a for a, r in ARMS.items() if r["stage"] == "production" and r["validator_mode"] == "real_ld"]
    t["e5_diagnostics"] = estimands.e5_diagnostics(fits[fits.arm.isin(real_ld)])
    t["e6_panel_contrast"] = estimands.e6_panel_contrast(rows, fits, rules, ids, E6, P12_KEYS)

    layer, qdocs, tiers_frozen, tiers_fixed = _qtl(repo)
    a3_arm = {anc: arm for arm, anc in A1_FIT_ARMS.items()}
    t["e7_frozen_vs_fixed"] = estimands.e7_frozen_vs_fixed(
        _read_tsv(Path(repo) / KNOWN_W3A), _read_tsv(Path(repo) / KNOWN_SH2B3), fits, rows, qdocs, a3_arm=a3_arm,
        p12_key=conf["rows"]["p12_key"], qtl_tiers_frozen=tiers_frozen, qtl_tiers_fixed=tiers_fixed)
    t["e8_simulation_rates"] = _e8(repo, rules, final=final)
    afr_ids = _ids(man, rules, ancestry="AFR")
    t["afr_secondary"] = estimands.e6_panel_contrast(rows, fits, rules, afr_ids, AFR, P12_KEYS)
    t["negative_controls"] = estimands.negative_control_rates(rows, float(rules["threshold_primary"]))
    t["qtl_layer"] = layer
    t["min_abs_corr_sweep"] = estimands.min_abs_corr_sweep(fits)
    hla = fits[(fits.arm == HLA[0]) & (fits.region_safe == HLA[1])]
    t["hla_exploratory"] = hla[["arm", "trait", "ancestry", "region_safe", "status", "n_cs", "cs_sizes"]].assign(
        note=HLA_NOTE)
    t1 = man.groupby(["ancestry", "row_class", "admissible"]).agg(
        n_rows=("row_id", "size"), n_regions=("region_safe", "nunique")).reset_index()
    obs = rows.groupby(["ancestry", "row_class", "admissible"]).row_id.nunique().rename("n_rows_with_outputs")
    t["table1_data"] = t1.merge(obs.reset_index(), on=["ancestry", "row_class", "admissible"], how="left").fillna(
        {"n_rows_with_outputs": 0}).astype({"n_rows_with_outputs": int})
    drops = [estimands.row_drop_table(rows, man[man.row_id.isin(ids)],
                                      [(n.split("_vs_")[0], ref, "confirmatory", conf["both_have_cs"][n])], P12_KEYS,
                                      a1_varset=a1v).assign(family="confirmatory") for n in conf["contrasts"]]
    drops.append(estimands.row_drop_table(rows, man[man.row_id.isin(ids)], E6, P12_KEYS).assign(family="e6"))
    drops.append(estimands.row_drop_table(rows, man[man.row_id.isin(afr_ids)], AFR, P12_KEYS).assign(
        family="afr_secondary"))
    rd = pd.concat(drops, ignore_index=True)
    nc = [c for c in rd.columns if c.startswith("n_none_")]
    rd[nc] = rd[nc].fillna(0).astype(int)
    t["row_drops"] = rd[["family", *[c for c in rd.columns if c != "family"]]]
    t["qtl_rows"] = _qtl_rows(repo)
    return t


def _coverage(repo, man):
    """(header text, {ancestry: (missing, extra)}) from coloc_coverage for EUR and AFR."""
    res = {a: coloc_coverage.check(coloc_coverage.expected_ids(man, a), repo) for a in ("EUR", "AFR")}
    return "; ".join(f"{a} missing={len(m)} extra={len(x)}" for a, (m, x) in res.items()), res


def run_aggregation(repo, out_dir, *, draft=False, purity_runner=_rscript_purity) -> int:
    repo, out_dir = Path(repo), Path(out_dir)
    status = estimands.output_status(repo)
    if status != "FINAL" and not draft:
        print("run_aggregation: status DRAFT (a config is unlocked, the W4a-T3 sign-off is missing or does not match,"
              " or the offline lock gate fails); nothing written", file=sys.stderr)
        return 2
    if draft:
        status = "DRAFT"
    rules = estimands.load_rules(repo)
    man = estimands.load_manifest(repo)
    cov, res = _coverage(repo, man)
    print(f"run_aggregation: coverage {cov}", file=sys.stderr)
    paths_off = [f"{tag} {p}" for m, x in res.values() for tag, s in (("MISSING", m), ("EXTRA", x)) for p in sorted(s)]
    if paths_off:
        print("\n".join(paths_off[:20]), file=sys.stderr)
        if not draft:
            print("run_aggregation: FINAL refused, coloc coverage incomplete; nothing written", file=sys.stderr)
            return 3
    qmiss = _qtl_missing(repo)
    if qmiss:
        print("\n".join(f"MISSING {p}" for p in qmiss), file=sys.stderr)
        if not draft:
            print("run_aggregation: FINAL refused, QTL summary or tier table missing; nothing written", file=sys.stderr)
            return 3
    try:
        tables = build_tables(repo, rules, man, estimands.load_rows(repo, man), estimands.load_fits(repo), purity_runner,
                              final=not draft)
    except estimands.SimulationIncomplete as e:
        print(f"run_aggregation: {e}; nothing written", file=sys.stderr)
        return 3
    if tuple(tables) != TABLES:
        raise RuntimeError(f"table set {sorted(tables)} != TABLES")
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in TABLES:
        with open(out_dir / f"{name}.tsv", "w") as fh:
            fh.write(f"# status={status}\n# coverage={cov}\n")
            tables[name].to_csv(fh, sep="\t", index=False, na_rep="NA")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m ta_r4.run_aggregation", description=__doc__)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--draft", action="store_true", help="fixtures only: label every table DRAFT; W7 never passes it")
    a = ap.parse_args(argv)
    return run_aggregation(a.repo, a.out, draft=a.draft)


if __name__ == "__main__":
    sys.exit(main())
