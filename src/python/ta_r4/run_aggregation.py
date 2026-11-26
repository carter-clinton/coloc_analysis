"""The single entry point for every R4 table (W7 runs it; written and frozen in W3d).

Reads trait-pair coloc JSONs only from paths.result_dirs('coloc') and fits only from result_dirs('fits'); the E7
frozen side comes from the committed known-answer tables and the QTL_legacy tier table by explicit path. Every
statistic comes from estimands / branch_classifier. Exits 2 and writes nothing unless estimands.output_status
is FINAL; exits 3 and writes nothing if FINAL and coloc_coverage finds a missing or extra output (EUR or AFR) or a
QTL arm's summary or tier table is missing or its rows (or the QTL_A3 JSON docs) do not reconcile with qtl_manifest.tsv
by id, or if FINAL and a cross-purity fit's JSON records a catalog or panel other than the one it is resolved with;
exits 3 (FINAL and DRAFT) unless every simulation.yaml cell is present and matches its design by identity;
--draft (fixtures only) writes every table labelled DRAFT. Every table carries a coverage header line.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd
import yaml

from ta_r4 import branch_classifier, coloc_coverage, estimands, paths
from ta_r4.arms import ARMS
from ta_r4.commands import A1_FIT_ARMS, P12_KEYS
from ta_r4.id_reconcile import reconcile, stable_index

TABLES = ("branch_outcomes", "e1_paired_delta", "e2_agreement_sweep", "e3_reclassification", "e4_finemap_structure",
          "e4_no_cs_rate", "e4_cross_purity", "e5_diagnostics", "e6_panel_contrast", "e7_frozen_vs_fixed",
          "e8_simulation_rates", "afr_secondary", "a1_allvars_secondary", "negative_controls", "qtl_layer",
          "min_abs_corr_sweep", "hla_exploratory", "table1_data", "row_drops", "qtl_rows")
KNOWN_W3A = f"{paths.MAN}/known_answer_W3a.tsv"
KNOWN_SH2B3 = f"{paths.MAN}/known_answer_sh2b3.tsv"
FIT_CS_FILTERED = f"{paths.MAN}/fit_cs_json_vs_rds.tsv"
SIM_DIR = f"{paths.R4}/results/sim"
SIM_CFG = "config/ta_r4/simulation.yaml"
SIM_ARMS = ("A1", "A2", "A3")
QTL_ARMS = ("QTL_A3", "QTL_A2", "QTL_legacy")
QTL_TIERS = f"{paths.R4}/results/{{arm}}/qtl_tiers.tsv"
QTL_SUMMARY = f"{paths.R4}/results/{{arm}}/qtl_coloc_summary.tsv"  # aggregate_qtl_coloc --with-method-columns
QTL_JSON_DIR = f"{paths.R4}/results/QTL_A3/qtl"
QTL_MANIFEST = "config/ta_r4/qtl_manifest.tsv"  # harmonize_qtl_r4.MANIFEST
QTL_PP_COLS = ["PP.H0.abf", "PP.H1.abf", "PP.H2.abf", "PP.H3.abf", "PP.H4.abf"]  # aggregate_qtl_coloc.SUMMARY_PP_COLS
CODE_ROOT = Path(__file__).resolve().parents[3]  # the repo holding src/python/assign_tiers.py
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
#: A1 on all variants, secondary and descriptive (D-21): EUR on the confirmatory row ids, AFR on the AFR ids
A1_ALLVARS_EUR = (("A1_allvars", "A3_1kg", "allvars", "A3_1kg method coloc_susie"),)
A1_ALLVARS_AFR = (("A1_allvars", "AFR661_A3", "allvars", "AFR661_A3 method coloc_susie"),)
HLA = ("A3_ukb", "HLA_6p21")
HLA_NOTE = "exploratory A3_ukb fit; no coloc row: no admissible comparator panel (D-24)"
PURITY_COLS = ["fit_arm", "panel_arm", "fit_status", "trait", "ancestry", "region_safe", "cs", "size",
               "n_cs_variants", "n_present", "min_abs_corr", "mean_abs_corr", "purity_fit", "note",
               "n_route_sumstats", "n_route_panel", "n_route_chrpos", "n_match_exact", "n_match_swapped",
               "n_match_strand", "n_refused_multi_key"]


class CrossPurityInputMismatch(RuntimeError):
    """A fit's JSON records a variant catalog or LD panel other than the one cross-purity would resolve it with."""


def _rscript_purity(repo, fit_rds, panel_rds, allow_absent, *, fit_sumstats, fit_catalog, region_safe, regions_csv,
                    fit_panel):
    """cs_cross_purity.R on one fit: members resolve through the fit's sumstats, catalog and panel (15.7c, F10).
    Never passes --allow-duplicate-rows (production fits)."""
    from ta_r4.run_qtl_group_r4 import region_ids

    region_id = region_ids(regions_csv)[region_safe]
    tmp = Path(repo) / paths.R4 / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=tmp) as td:
        out = Path(td) / "cross_purity.tsv"
        subprocess.run([RSCRIPT, str(Path(repo) / CROSS_PURITY_R), "--fit", str(fit_rds), "--panel", str(panel_rds),
                        "--output", str(out), "--fit-sumstats", str(fit_sumstats), "--fit-catalog", str(fit_catalog),
                        "--region-id", region_id, "--regions-csv", str(regions_csv), "--fit-panel", str(fit_panel),
                        *(["--allow-absent"] if allow_absent else [])],
                       check=True, capture_output=True, text=True)
        return pd.read_csv(out, sep="\t", keep_default_na=False, na_values=["NA"])


def _real(repo, p):
    p = Path(p)
    return os.path.realpath(p if p.is_absolute() else Path(repo) / p)


def _fit_input_problems(repo, fit_arm, f, catalog, fit_panel):
    """Differences between the catalog / panel cross-purity uses and those the fit JSON records (real paths)."""
    js = Path(repo) / paths.fit_json(fit_arm, f.trait, f.ancestry, f.region_safe)
    if not js.exists():
        return [f"no fit JSON {js}"]
    d = json.loads(js.read_text())
    out = []
    rec = d.get("variant_catalog_path")
    if not rec or _real(repo, rec) != _real(repo, catalog):
        out.append(f"variant_catalog_path {rec} != {catalog}")
    rec = d.get("ld_file_declared") or d.get("ld_matrix")
    if not rec or _real(repo, rec) != _real(repo, fit_panel):
        out.append(f"fit panel {rec} != {fit_panel}")
    return out


def _cross_purity(repo, fits, runner, final=True):
    """Every fit of each fit arm, whatever its status. Fits that exited early, have no RDS / panel, or whose RDS has
    no credible set get one row with a note; a fit with sets gets one row per set. Each scored fit's JSON must record
    the catalog paths.catalog_path(route, region) and the panel paths.panel_path(fit_arm, region): otherwise FINAL
    raises CrossPurityInputMismatch naming the fit and DRAFT prints it and scores nothing (note fit_inputs_mismatch)."""
    out = []
    regions_csv = Path(repo) / paths.regions_csv()
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
            fit_panel = Path(repo) / paths.panel_path(fit_arm, f.region_safe)
            catalog = Path(repo) / paths.catalog_path(ARMS[fit_arm]["route"], f.region_safe)
            bad = _fit_input_problems(repo, fit_arm, f, catalog, fit_panel)
            if bad:
                msg = f"cross-purity {fit_arm} {f.trait}.{f.ancestry}.{f.region_safe}: " + "; ".join(bad)
                if final:
                    raise CrossPurityInputMismatch(msg)
                print(f"run_aggregation: DRAFT {msg}", file=sys.stderr)
                out.append({**key, "note": "fit_inputs_mismatch"})
                continue
            t = runner(repo, rds, panel, allow_absent,
                       fit_sumstats=Path(repo) / paths.sumstats_path(f.trait, f.ancestry, fit_arm),
                       fit_catalog=catalog, region_safe=f.region_safe, regions_csv=regions_csv, fit_panel=fit_panel)
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


def sim_header(text):
    """{key: value} from every `# ` line of a simulate_coloc_r4.R cell file, each line read as space-separated
    k=v tokens (tokens without `=` are skipped). A key given twice raises ValueError."""
    head = {}
    for ln in text.splitlines():
        if not ln.startswith("# "):
            continue
        for tok in ln[2:].split(" "):
            if "=" in tok:
                k, v = tok.split("=", 1)
                if k in head:
                    raise ValueError(f"header key {k!r} given twice")
                head[k] = v
    return head


def _sim_identity(name, df, cell, cfg, reps):
    """Problems of a status-ok cell: replicate ids per arm, row labels and seeds."""
    bad = []
    other = sorted(set(df.arm.astype(str)) - set(SIM_ARMS))
    if other:
        bad.append(f"{name}: arms {other} outside {SIM_ARMS}")
    rec = {a: reconcile(range(1, reps + 1), df.rep[df.arm == a].tolist()) for a in SIM_ARMS}
    if not all(r.ok for r in rec.values()):
        bad.append(f"{name}: rep ids per arm != 1..{reps} once each: "
                   + "; ".join(f"{a} {r.summary(5)}" for a, r in rec.items() if not r.ok))
    for col, want in zip(("region", "scenario", "gen_panel"), cell):
        off = df[df[col].astype(str) != want]
        if len(off):
            bad.append(f"{name}: {len(off)} row(s) with {col} != {want!r} (e.g. {off[col].iloc[0]!r})")
    seed_base = int(cfg["seed_base"])
    n_bad, first = 0, None
    for rep, seed in zip(df.rep.tolist(), df.seed.tolist()):
        try:
            k = int(rep)
        except (TypeError, ValueError):
            continue
        if k != rep or not 1 <= k <= reps:
            continue  # reported by the replicate-id check
        want = seed_base + stable_index(cfg, *cell, k)
        if seed != want:
            n_bad += 1
            first = first or f"rep {k} seed {seed!r} != {want}"
    if n_bad:
        bad.append(f"{name}: {n_bad} row(s) with seed != seed_base + stable_index (e.g. {first})")
    return bad


def _sim(repo, *, final):
    """Every expected cell file, read and checked by identity. Every file: header region / scenario / gen_panel equal
    the cell and header config_sha256 equals the sha256 of the repo's simulation.yaml. Status ok: per arm (A1, A2,
    A3) the rep ids are exactly 1..reps once each, every row's labels equal the cell, every seed equals seed_base +
    stable_index(cell, rep), header reps equals reps and, in FINAL, reps_override=none. Status no_qualifying_pair: 0
    rows. A missing, extra or failing file raises SimulationIncomplete."""
    cells, reps = expected_sim_cells(repo)
    cfg_bytes = (Path(repo) / SIM_CFG).read_bytes()
    cfg, cfg_sha = yaml.safe_load(cfg_bytes), hashlib.sha256(cfg_bytes).hexdigest()
    files = {p.name: p for p in (Path(repo) / SIM_DIR).glob("*.tsv")}
    bad = [f"missing {n}" for n in sorted(set(cells) - set(files))]
    bad += [f"extra {n}" for n in sorted(set(files) - set(cells))]
    frames, meta = [], []
    for name in sorted(set(cells) & set(files)):
        p = files[name]
        try:
            head = sim_header(p.read_text())
        except ValueError as e:
            bad.append(f"{name}: {e}")
            head = {}
        status, override = head.get("status", ""), head.get("reps_override", "")
        for k, want in zip(("region", "scenario", "gen_panel"), cells[name]):
            if head.get(k) != want:
                bad.append(f"{name}: header {k}={head.get(k)!r} != {want!r}")
        if "config_sha256" not in head:
            bad.append(f"{name}: no config_sha256 in the header")
        elif head["config_sha256"] != cfg_sha:
            bad.append(f"{name}: header config_sha256 {head['config_sha256']} != sha256({SIM_CFG}) {cfg_sha}")
        df = pd.read_csv(p, sep="\t", comment="#")
        if status == "ok":
            n_arm = df.arm.value_counts().to_dict() if len(df) else {}
            if n_arm != {a: reps for a in SIM_ARMS}:
                bad.append(f"{name}: rows per arm {n_arm} != {reps} x {SIM_ARMS}")
            elif len(df):
                bad += _sim_identity(name, df, cells[name], cfg, reps)
            if head.get("reps") != str(reps):
                bad.append(f"{name}: header reps={head.get('reps')!r} != {reps}")
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


def _qtl_tiers_qtl4dp(repo):
    """QTL_A3's tier table re-derived from its posteriors rounded as jsonlite's default writes them (E7
    fixed_value_qtl_4dp): PP.H0.abf … PP.H4.abf of a temporary copy of QTL_A3's qtl_coloc_summary_tierable.tsv are
    rounded by estimands.round_like_jsonlite_default, then assign_tiers.py runs with QTL_A3's own argv
    (run_qtl_group_r4.tiers_argv) and QTL_A3's GWAS table and pph4 config; every output is in the temporary directory.
    None when QTL_A3's tierable summary is absent."""
    import csv

    from ta_r4 import run_qtl_group_r4

    repo = Path(repo).resolve()
    d = repo / QTL_TIERS.format(arm="QTL_A3").rsplit("/", 1)[0]
    summary, gwas = d / "qtl_coloc_summary_tierable.tsv", d / "gwas_coloc_for_tiers.tsv"
    if not summary.exists():
        return None
    if not gwas.exists():
        raise FileNotFoundError(f"{gwas}: QTL_A3's GWAS table is needed to re-derive its 4-decimal tiers")
    with tempfile.TemporaryDirectory(prefix="qtl4dp_") as tmp:
        tmp = Path(tmp)
        with open(summary, newline="") as fh:
            rows = list(csv.reader(fh, delimiter="\t"))
        idx = [rows[0].index(c) for c in QTL_PP_COLS]
        for r in rows[1:]:
            for i in idx:
                if r[i] not in ("", "NA", "nan", "NaN"):
                    r[i] = repr(estimands.round_like_jsonlite_default(float(r[i])))
        with open(tmp / "summary_4dp.tsv", "w", newline="") as fh:
            csv.writer(fh, delimiter="\t", lineterminator="\n").writerows(rows)
        argv = run_qtl_group_r4.tiers_argv("QTL_A3", str(tmp / "summary_4dp.tsv"), str(gwas),
                                           str(repo / "config/pph4_thresholds.yaml"), str(tmp / "tiers_4dp.tsv"),
                                           str(tmp / "tiers_4dp_sweep.tsv"))
        p = subprocess.run(argv, cwd=CODE_ROOT, capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError(f"assign_tiers.py on the 4-decimal QTL_A3 copy failed: {p.stderr[-2000:]}")
        return _read_tsv(tmp / "tiers_4dp.tsv")


def _qtl_rows(repo):
    """Every row of each QTL arm's qtl_coloc_summary.tsv (coloc_susie, fallback_abf and none), with qtl_arm."""
    t = [_read_tsv(p).assign(qtl_arm=a) for a in QTL_ARMS
         for p in [Path(repo) / QTL_SUMMARY.format(arm=a)] if p.exists()]
    t = pd.concat(t, ignore_index=True) if t else pd.DataFrame(columns=["qtl_coloc_id"]).assign(qtl_arm=None)
    return t[["qtl_arm", *[c for c in t.columns if c != "qtl_arm"]]]


def _qtl_doc_ids(repo):
    qdir = Path(repo) / QTL_JSON_DIR
    return [str(p.relative_to(qdir))[: -len(".json")] for p in sorted(qdir.rglob("*.json"))] if qdir.is_dir() else []


def _qtl_coverage(repo):
    """Problems ([] = complete): per QTL arm, the summary and tier table exist, the summary's qtl_coloc_id equal
    qtl_manifest.tsv's qtl_row_id exactly once each and no row has an empty method; the QTL_A3 JSON doc ids (those
    _qtl reads for E7) equal the manifest ids too."""
    repo = Path(repo)
    out = [f"MISSING {p}" for a in QTL_ARMS for p in (QTL_SUMMARY.format(arm=a), QTL_TIERS.format(arm=a))
           if not (repo / p).exists()]
    if not (repo / QTL_MANIFEST).exists():
        return out + [f"MISSING {QTL_MANIFEST}"]
    expected = _read_tsv(repo / QTL_MANIFEST).qtl_row_id.tolist()
    for a in QTL_ARMS:
        p = repo / QTL_SUMMARY.format(arm=a)
        if not p.exists():
            continue
        t = _read_tsv(p)
        if not {"qtl_coloc_id", "method"} <= set(t.columns):
            out.append(f"{a} summary: no qtl_coloc_id / method column")
            continue
        r = reconcile(expected, t.qtl_coloc_id.tolist())
        if not r.ok:
            out.append(f"{a} summary vs {QTL_MANIFEST}: {r.summary()}")
        empty = t.qtl_coloc_id[t.method == ""].tolist()
        if empty:
            out.append(f"{a} summary: {len(empty)} row(s) with an empty method: " + ", ".join(empty[:10]))
    r = reconcile(expected, _qtl_doc_ids(repo))
    if not r.ok:
        out.append(f"QTL_A3 JSON docs ({QTL_JSON_DIR}) vs {QTL_MANIFEST}: {r.summary()}")
    return out


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
    t["e4_cross_purity"] = _cross_purity(repo, fits, purity_runner, final=final)
    real_ld = [a for a, r in ARMS.items() if r["stage"] == "production" and r["validator_mode"] == "real_ld"]
    t["e5_diagnostics"] = estimands.e5_diagnostics(fits[fits.arm.isin(real_ld)])
    t["e6_panel_contrast"] = estimands.e6_panel_contrast(rows, fits, rules, ids, E6, P12_KEYS)

    layer, qdocs, tiers_frozen, tiers_fixed = _qtl(repo)
    a3_arm = {anc: arm for arm, anc in A1_FIT_ARMS.items()}
    t["e7_frozen_vs_fixed"] = estimands.e7_frozen_vs_fixed(
        _read_tsv(Path(repo) / KNOWN_W3A), _read_tsv(Path(repo) / KNOWN_SH2B3), fits, rows, qdocs, a3_arm=a3_arm,
        p12_key=conf["rows"]["p12_key"], fit_cs_filtered=_read_tsv(Path(repo) / FIT_CS_FILTERED),
        qtl_tiers_frozen=tiers_frozen, qtl_tiers_fixed=tiers_fixed,
        qtl_tiers_fixed_4dp=_qtl_tiers_qtl4dp(repo))
    t["e8_simulation_rates"] = _e8(repo, rules, final=final)
    afr_ids = _ids(man, rules, ancestry="AFR")
    t["afr_secondary"] = estimands.e6_panel_contrast(rows, fits, rules, afr_ids, AFR, P12_KEYS)
    av = [estimands.e6_panel_contrast(rows, fits, rules, i, c, P12_KEYS).assign(ancestry=anc)
          for anc, i, c in (("EUR", ids, A1_ALLVARS_EUR), ("AFR", afr_ids, A1_ALLVARS_AFR))]
    av = pd.concat(av, ignore_index=True)
    t["a1_allvars_secondary"] = av[["ancestry", *[c for c in av.columns if c != "ancestry"]]]
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
    drops += [estimands.row_drop_table(rows, man[man.row_id.isin(i)], c, P12_KEYS).assign(family="a1_allvars")
              for i, c in ((ids, A1_ALLVARS_EUR), (afr_ids, A1_ALLVARS_AFR))]
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
    qprob = _qtl_coverage(repo)
    if qprob:
        print("\n".join(qprob), file=sys.stderr)
        if not draft:
            print("run_aggregation: FINAL refused, QTL summary or tier table missing or QTL rows do not reconcile with"
                  " the manifest; nothing written", file=sys.stderr)
            return 3
    try:
        tables = build_tables(repo, rules, man, estimands.load_rows(repo, man), estimands.load_fits(repo), purity_runner,
                              final=not draft)
    except (estimands.SimulationIncomplete, CrossPurityInputMismatch) as e:
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
