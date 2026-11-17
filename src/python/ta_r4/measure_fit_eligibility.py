"""W3f 15.5: measure post-restriction variant counts without fitting (review N1 recount), and the
confirmatory-region contribution proxy from existing repro fits (N7). Pre-lock, read-only on inputs.

measurement_argv() is commands.fit_command() with three changes: SUSIE_MAX_VARIANTS=0 (every fit early-exits
after the panel restriction), an absolute Rscript, and an --output under data/r4/tmp/. It refuses anything else.

CLI (cwd = repo root, PYTHONPATH=src/python):
  plan      --out-dir D --rscript R               write D/runlist.jsonl + D/run.sh (sbatch array), print its length
  run       --list L --task N                     record input sha256, then run line N (1-based) of the list
  summarise --out-dir D --rscript R --tsv T       eligibility table: measured rows (exactly the run list) + bound rows
  proxy     --rscript R --tsv T                   region-contribution proxy table, totals and FLAG lines
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import posixpath
import subprocess
import sys
from pathlib import Path

from ta_r4 import commands, paths, verify_inputs
from ta_r4.arms import ARMS, production_arms

CAP = commands.SUSIE_MAX_VARIANTS
TMP = f"{paths.R4}/tmp"
FLAG = "--cap-after-ld-restriction"
EARLY = ("no_variants", "too_many_variants")
PAIR_MANIFEST = "config/ta_r4/pair_manifest.tsv"
#: The review's regression pair (W4a disposition: asthma x PYHIN1_1q23 38,313 catalog-joined rows) and its T2D twin.
REGRESSION_KEYS = (("A3_1kg", "asthma", "EUR", "PYHIN1_1q23"), ("A3_1kg", "t2d", "EUR", "PYHIN1_1q23"))
#: The pre-fix recount arm: the pre-LD (catalog-join) count is arm-independent across EUR r4 arms.
PRE_FIX_ARM = "A3_1kg"
INPUT_FLAGS = ("--sumstats", "--regions-csv", "--ld-dir", "--ld-file", "--variant-list", "--policy")
#: Inputs whose sha256 each measurement records in-job: argv flag -> pinned_inputs() key.
RECORDED_INPUTS = {"--sumstats": "sumstats", "--variant-list": "catalog", "--ld-file": "panel"}
ELIG_COLS = ["arm", "trait", "ancestry", "region_safe", "panel_n_var", "status", "n_variants_pre_ld", "n_variants",
             "cap_stage", "eligible", "method", "sumstats_sha256", "catalog_sha256", "panel_sha256"]
#: Proxy arms: repro_routeC (real LD) for A3, repro_k2d_routeC (identity) for A2 (W3a repro fits, pre-lock).
PROXY = {"A1_matched_vs_A3_1kg": ("repro_routeC",), "A2_identity_vs_A3_1kg": ("repro_routeC", "repro_k2d_routeC")}
#: Repro coloc arms whose outputs give the discordance proxy (X, reference); A1 has no repro analogue.
PROXY_COLOC = {"A2_identity_vs_A3_1kg": ("repro_k2d_routeC", "repro_routeC")}
#: Repro fits read the earlier asthma EUR file (GRCh38 positions labelled GRCh37; debug asthma-eur-grch38-mislabel).
PROXY_EXCLUDED_TRAITS = ("asthma",)
PROXY_COLS = ["region", "contrast", "n_pairs", "n_pairs_asthma_excluded", "n_pairs_both_cs_proxy", "n_pairs_unknown",
              "classification", "discordant_proxy", "source_arms"]
THRESHOLD_PRIMARY = 0.8
N_REGIONS_MIN = 7


class FitHappened(RuntimeError):
    """A measurement output is not an early exit (a fit ran, or its record is incomplete)."""


class MeasurementSetError(ValueError):
    """The measured set is not exactly the run list, or a measurement lacks its input record."""


class BoundViolation(ValueError):
    """A measured post-restriction count exceeds its panel n_var or its pre-restriction count."""


class InputMismatch(ValueError):
    """A measurement read an input whose sha256 is not the committed pin."""


def _norm(p):
    return posixpath.normpath(str(p))


def _under(p, d):
    p, d = _norm(p), _norm(d)
    return p == d or p.startswith(d + "/")


def measurement_output(out_dir, arm, trait, ancestry, region_safe):
    return f"{_norm(out_dir)}/{arm}/{trait}.{ancestry}.{region_safe}.json"


def measurement_argv(arm, trait, ancestry, region_safe, config, out_dir, rscript, *, region_id=None):
    out_dir = _norm(out_dir)
    if not _under(out_dir, TMP) or out_dir == TMP:
        raise ValueError(f"out_dir {out_dir!r} must lie under {TMP}/")
    cmd = list(commands.fit_command(arm, trait, ancestry, region_safe, config, region_id=region_id))
    if FLAG not in cmd or cmd[cmd.index(FLAG) + 1] != "true":
        raise ValueError(f"{arm}: fit_command has no {FLAG} true; a pre-LD cap cannot measure post-restriction n")
    out = measurement_output(out_dir, arm, trait, ancestry, region_safe)
    for d in paths.result_dirs("fits") + paths.result_dirs("coloc"):
        if _under(out, d):
            raise ValueError(f"output {out} lies in result dir {d}")
    cap = f"SUSIE_MAX_VARIANTS={CAP}"
    if cmd[1] != cap or cmd[2] != "Rscript":
        raise ValueError(f"unexpected fit_command prefix {cmd[:3]}")
    cmd[1], cmd[2] = "SUSIE_MAX_VARIANTS=0", rscript
    cmd[cmd.index("--output") + 1] = out
    return cmd


def audit_argv(argv, out_dir, arm, repo="."):
    """Violations of: every path argument is a read-only input (an existing file, or ld_dir_unused() absent),
    or the single --output under out_dir; nothing under a result dir."""
    repo = Path(repo)
    bad = []
    script = argv[3]
    vals = [("script", script)] + [(f, argv[argv.index(f) + 1]) for f in INPUT_FLAGS if f in argv]
    out = argv[argv.index("--output") + 1]
    result = paths.result_dirs("fits") + paths.result_dirs("coloc")
    for flag, v in vals:
        if _under(v, out_dir):
            bad.append(f"{flag} {v} lies under out_dir")
        elif any(_under(v, d) for d in result):
            bad.append(f"{flag} {v} lies in a result dir")
        elif flag == "--ld-dir":
            if v != paths.ld_dir_unused() or (repo / v).exists():
                bad.append(f"--ld-dir {v} is not the absent ld_dir_unused()")
        elif not (repo / v).is_file():
            bad.append(f"{flag} {v} is not an existing input file")
    if not _under(out, out_dir):
        bad.append(f"--output {out} is not under {out_dir}")
    if any(_under(out, d) for d in result):
        bad.append(f"--output {out} lies in a result dir")
    return bad


def arm_config(arm, repo="."):
    """config/pipeline.yaml + overlay_base + overlay_<arm>, Snakemake update_config semantics (as the rule)."""
    import yaml
    from snakemake.utils import update_config

    repo = Path(repo)
    cfg = yaml.safe_load((repo / "config/pipeline.yaml").read_text())
    for p in ("config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{arm}.yaml"):
        update_config(cfg, yaml.safe_load((repo / p).read_text()) or {})
    return cfg


def _manifest(repo="."):
    with open(Path(repo) / PAIR_MANIFEST, newline="") as fh:
        return [r for r in csv.DictReader(fh, delimiter="\t") if r["admissible"] == "true"]


def region_ids(repo="."):
    ids = {}
    for r in _manifest(repo):
        if commands.safe_region_id(r["region_id"]) != r["region_safe"]:
            raise ValueError(f"{r['row_id']}: region_safe {r['region_safe']} != safe({r['region_id']})")
        ids[r["region_safe"]] = r["region_id"]
    return ids


def fit_keys(repo="."):
    """(production arm, trait, ancestry, region_safe) for every trait of every admissible pair_manifest row."""
    keys = set()
    for r in _manifest(repo):
        for arm in production_arms(r["ancestry"]):
            for t in (r["trait_a"], r["trait_b"]):
                keys.add((arm, t, r["ancestry"], r["region_safe"]))
    return sorted(keys)


def pre_fix_keys(repo="."):
    """A3_1kg fits of every trait of every primary admissible EUR row (the review's N1 recount population)."""
    keys = {(PRE_FIX_ARM, t, "EUR", r["region_safe"]) for r in _manifest(repo)
            if r["row_class"] == "primary" and r["ancestry"] == "EUR" for t in (r["trait_a"], r["trait_b"])}
    return sorted(keys)


def _panel_rows(repo="."):
    """{(panel_dir, ancestry, region_safe): manifest row} from every production arm's panel manifest."""
    out = {}
    for arm in production_arms():
        mp = Path(repo) / paths.panel_manifest_path(arm, ARMS[arm]["ancestry"])
        with open(mp, newline="") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                out[(ARMS[arm]["panel_dir"], r["ancestry"], r["region_safe"])] = r
    return out


def panel_n_var(repo="."):
    """{(panel_dir, ancestry, region_safe): n_var} from every production arm's panel manifest."""
    return {k: int(r["n_var"]) for k, r in _panel_rows(repo).items()}


def _n_var(key, nvar):
    return nvar[(ARMS[key[0]]["panel_dir"], key[2], key[3])]


def run_list(repo=".", *, nvar=None, fits=None, extra=None):
    """Fits whose panel n_var is strictly above CAP (they can early-exit), plus `extra` (default: the regression
    pair and the pre-fix recount population, measured as checks of the bound)."""
    nvar = panel_n_var(repo) if nvar is None else nvar
    fits = fit_keys(repo) if fits is None else fits
    extra = (*REGRESSION_KEYS, *pre_fix_keys(repo)) if extra is None else extra
    return sorted({k for k in fits if _n_var(k, nvar) > CAP} | set(extra))


def pinned_inputs(key, repo="."):
    """Committed sha256 of the sumstats, catalog and panel a production fit `key` reads."""
    arm, trait, anc, reg = key
    sp, cp = paths.sumstats_path(trait, anc, arm), paths.catalog_path(ARMS[arm]["route"], reg)
    pp = paths.panel_path(arm, reg, anc)
    rec = verify_inputs.recorded((verify_inputs.SUMSTATS, verify_inputs.CATALOGS), repo)
    prow = _panel_rows(repo).get((ARMS[arm]["panel_dir"], anc, reg))
    if sp not in rec or cp not in rec or prow is None:
        raise InputMismatch(f"{key}: no committed pin for {[p for p in (sp, cp) if p not in rec] or pp}")
    if _norm(prow["path"]) != _norm(pp):
        raise InputMismatch(f"{key}: panel manifest path {prow['path']} != {pp}")
    return {"sumstats_path": sp, "sumstats": rec[sp], "catalog_path": cp, "catalog": rec[cp],
            "panel_path": pp, "panel": prow["sha256"]}


def inputs_record_path(output_json):
    return str(output_json)[: -len(".json")] + ".inputs.json"


def write_inputs_record(argv, repo="."):
    """sha256 of the sumstats, catalog and panel bytes the measurement reads, next to its --output."""
    rec = {}
    for flag, k in RECORDED_INPUTS.items():
        p = argv[argv.index(flag) + 1]
        rec[f"{k}_path"], rec[k] = p, verify_inputs.sha256_file(Path(repo) / p)
    out = Path(repo) / inputs_record_path(argv[argv.index("--output") + 1])
    out.write_text(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def eligible(n_variants):
    return int(n_variants) <= CAP


def _sha_cols(inputs):
    return {"sumstats_sha256": inputs["sumstats"], "catalog_sha256": inputs["catalog"],
            "panel_sha256": inputs["panel"]}


def bound_row(key, n_var, inputs):
    if n_var > CAP:
        raise ValueError(f"{key}: panel n_var {n_var} is above the cap {CAP}; it must be measured")
    return {**dict(zip(ELIG_COLS, (*key, n_var, "", "", "", "", "true", "bound"))), **_sha_cols(inputs)}


_RDS_R = r"""
for (p in commandArgs(TRUE)) {
  f <- readRDS(p)
  st <- if (is.list(f) && !is.null(f$status)) as.character(f$status)[1] else "NA"
  writeLines(paste(p, as.integer(is.list(f) && !is.null(f$lbf_variable)), st, sep = "\t"))
}
"""


def _rds_probe(rscript, rds_paths):
    """{path: (has lbf_variable, status or 'NA')}."""
    if not rds_paths:
        return {}
    out = subprocess.run([rscript, "-e", _RDS_R, *map(str, rds_paths)], check=True, capture_output=True,
                         text=True).stdout
    return {p: (v == "1", s) for p, v, s in (ln.split("\t") for ln in out.splitlines())}


def _measurement_jsons(out_dir):
    return sorted(j for j in Path(out_dir).glob("*/*.json") if not j.name.endswith(".inputs.json"))


def summarise(out_dir, rscript, keys):
    """Rows of the measurements in out_dir, which must be exactly `keys` (the run list). Raises FitHappened unless
    each is an early exit whose .fit.rds exists, has no lbf_variable and carries the same status;
    MeasurementSetError on a missing or extra measurement or a missing input record."""
    want = set(keys)
    docs, found = [], set()
    for j in _measurement_jsons(out_dir):
        trait, anc, reg = j.name[: -len(".json")].split(".", 2)
        k = (j.parent.name, trait, anc, reg)
        found.add(k)
        if k not in want:
            continue
        rds = j.with_name(j.name[: -len(".json")] + ".fit.rds")
        if not rds.is_file():
            raise FitHappened(f"{j}: no sibling .fit.rds")
        inp = Path(inputs_record_path(j))
        if not inp.is_file():
            raise MeasurementSetError(f"{j}: no inputs record {inp.name}")
        docs.append((k, json.loads(j.read_text()), rds, json.loads(inp.read_text())))
    extra = sorted(found - want)
    if extra:
        raise MeasurementSetError(f"{len(extra)} measurements are not in the run list: {extra[:5]}")
    missing = sorted(want - found)
    if missing:
        raise MeasurementSetError(f"{len(missing)} run-list keys have no measurement: {missing[:5]}")
    probe = _rds_probe(rscript, [d[2] for d in docs])
    rows = []
    for k, d, rds, inputs in docs:
        lbf, rds_status = probe[str(rds)]
        if lbf:
            raise FitHappened(f"{rds}: has lbf_variable (a fit ran)")
        if d.get("status") not in EARLY:
            raise FitHappened(f"{k}: status {d.get('status')!r} is not an early exit")
        if rds_status != d["status"]:
            raise FitHappened(f"{rds}: RDS status {rds_status!r} != JSON status {d['status']!r}")
        if d["status"] == "too_many_variants" and (d.get("cap_stage") != "after_ld_restriction"
                                                   or int(d.get("n_variants", 0)) < 1):
            raise FitHappened(f"{k}: too_many_variants without a post-restriction count ({d.get('cap_stage')!r})")
        rows.append({"arm": k[0], "trait": k[1], "ancestry": k[2], "region_safe": k[3], "status": d["status"],
                     "n_variants_pre_ld": d.get("n_variants_pre_ld"), "n_variants": d.get("n_variants", 0),
                     "cap_stage": d.get("cap_stage"), "inputs": inputs})
    return rows


def eligibility_table(measured, repo="."):
    """One row per fit_keys() key: measured rows (exactly the run list; bound- and pin-checked) + bound rows."""
    nvar = panel_n_var(repo)
    want = set(run_list(repo))
    fits = fit_keys(repo)
    if not want <= set(fits):
        raise MeasurementSetError(f"run-list keys outside fit_keys(): {sorted(want - set(fits))[:5]}")
    by_key = {}
    for r in measured:
        k = (r["arm"], r["trait"], r["ancestry"], r["region_safe"])
        if k in by_key:
            raise MeasurementSetError(f"duplicate measurement {k}")
        by_key[k] = r
    extra = sorted(set(by_key) - want)
    if extra:
        raise MeasurementSetError(f"{len(extra)} measurements are not in the run list: {extra[:5]}")
    missing = sorted(want - set(by_key))
    if missing:
        raise MeasurementSetError(f"{len(missing)} run-list keys have no measurement: {missing[:5]}")
    out = []
    for k in fits:
        n_var, pin = _n_var(k, nvar), pinned_inputs(k, repo)
        if k not in by_key:
            out.append(bound_row(k, n_var, pin))
            continue
        r = by_key[k]
        n, pre = int(r["n_variants"]), r["n_variants_pre_ld"]
        if n > n_var:
            raise BoundViolation(f"{k}: n_variants {n} > panel n_var {n_var}")
        if pre is not None and n > int(pre):
            raise BoundViolation(f"{k}: n_variants {n} > n_variants_pre_ld {pre}")
        for c in ("sumstats", "catalog", "panel"):
            if r["inputs"].get(c) != pin[c] or r["inputs"].get(f"{c}_path", pin[f"{c}_path"]) != pin[f"{c}_path"]:
                raise InputMismatch(f"{k}: {c} read {r['inputs'].get(f'{c}_path')} sha256 {r['inputs'].get(c)}, "
                                    f"pinned {pin[f'{c}_path']} {pin[c]}")
        out.append({**dict(zip(ELIG_COLS, (*k, n_var, r["status"], pre, n, r["cap_stage"],
                                           str(eligible(n)).lower(), "measured"))), **_sha_cols(r["inputs"])})
    return out


# ---- region-contribution proxy ------------------------------------------------------------------------

def fit_cs_state(doc, n_sets):
    """None = unknown (absent or early-exit fit); else the number of purity-filtered sets (no $sets -> 0)."""
    if doc is None or doc.get("status") in EARLY:
        return None
    return int(n_sets or 0)


def pair_state(sides):
    """sides: fit_cs_state of every fit the contrast's both_have_cs needs."""
    if any(s == 0 for s in sides):
        return "not_both"
    if any(s is None for s in sides):
        return "unknown"
    return "both_cs"


def classify_region(states):
    if "both_cs" in states:
        return "likely"
    return "unknown" if "unknown" in states else "unlikely"


def confirmatory_pairs(repo="."):
    """{region_safe: [(trait_a, trait_b)]} of the confirmatory rows (primary, EUR, admissible)."""
    out = {}
    for r in _manifest(repo):
        if r["row_class"] == "primary" and r["ancestry"] == "EUR":
            if r["row_id"] != _row_id(r["region_safe"], r["trait_a"], r["trait_b"]):
                raise ValueError(f"row_id {r['row_id']} is not region__EUR__a_vs_b")
            out.setdefault(r["region_safe"], []).append((r["trait_a"], r["trait_b"]))
    return out


def _row_id(region_safe, a, b):
    return f"{region_safe}__EUR__{a}_vs_{b}"


def repro_coloc_json(arm, region_safe, a, b):
    """Where a repro arm's p12_primary coloc output for a confirmatory pair would be (paths.coloc_json)."""
    return paths.coloc_json(arm, _row_id(region_safe, a, b), "p12_primary")


def coloc_stat(doc):
    """region_stat of a both-have-CS (coloc_susie) output = pp_h4_max; None for anything else or absent."""
    if doc is None or doc.get("method") != "coloc_susie":
        return None
    v = doc.get("pp_h4_max")
    return None if v is None or (isinstance(v, float) and math.isnan(v)) else float(v)


def region_discordance(stats, threshold):
    """stats: (X, reference) region_stat per proxy pair. 'true' if some pair has the two on opposite sides of
    threshold (call = stat >= threshold); else 'unknown' if any side is missing or there are no pairs; else 'false'."""
    if any(x is not None and y is not None and (x >= threshold) != (y >= threshold) for x, y in stats):
        return "true"
    if not stats or any(x is None or y is None for x, y in stats):
        return "unknown"
    return "false"


_SETS_R = r"""
for (p in commandArgs(TRUE)) {
  f <- readRDS(p)
  writeLines(paste(p, if (is.list(f) && !is.null(f$sets)) length(f$sets$cs) else "NA", sep = "\t"))
}
"""


def _fit_states(rscript, keys, repo="."):
    repo = Path(repo)
    docs, rds = {}, {}
    for k in keys:
        j = repo / paths.fit_json(*k)
        docs[k] = json.loads(j.read_text()) if j.is_file() else None
        if docs[k] is not None and docs[k].get("status") not in EARLY:
            rds[k] = str(repo / paths.fit_rds(*k))
    out = subprocess.run([rscript, "-e", _SETS_R, *rds.values()], check=True, capture_output=True,
                         text=True).stdout if rds else ""
    by_path = dict(ln.split("\t") for ln in out.splitlines())
    return {k: fit_cs_state(docs[k], None if k not in rds or by_path[rds[k]] == "NA" else int(by_path[rds[k]]))
            for k in keys}


def _coloc_doc(repo, arm, region, a, b):
    p = Path(repo) / repro_coloc_json(arm, region, a, b)
    return json.loads(p.read_text()) if p.is_file() else None


def region_contribution_proxy(rscript, repo="."):
    """Per confirmatory region and contrast: proxy both-have-CS pairs from repro fits (asthma pairs excluded:
    their repro inputs are mislocated), classification, and the discordance proxy from repro coloc outputs."""
    pairs = confirmatory_pairs(repo)
    kept = {g: [p for p in ps if not set(p) & set(PROXY_EXCLUDED_TRAITS)] for g, ps in pairs.items()}
    keys = {(a, t, "EUR", g) for arms in PROXY.values() for a in arms for g, ps in kept.items() for p in ps for t in p}
    st = _fit_states(rscript, sorted(keys), repo)
    rows = []
    for g in sorted(pairs):
        for contrast, arms in PROXY.items():
            states = [(p, pair_state([st[(a, t, "EUR", g)] for a in arms for t in p])) for p in kept[g]]
            cl = classify_region([s for _, s in states])
            if cl == "unlikely":
                disc = "false"
            else:
                xr = PROXY_COLOC.get(contrast)
                stats = [(None, None) if xr is None else
                         (coloc_stat(_coloc_doc(repo, xr[0], g, *p)), coloc_stat(_coloc_doc(repo, xr[1], g, *p)))
                         for p, s in states if s in ("both_cs", "unknown")]
                disc = region_discordance(stats, THRESHOLD_PRIMARY)
            rows.append({"region": g, "contrast": contrast, "n_pairs": len(pairs[g]),
                         "n_pairs_asthma_excluded": len(pairs[g]) - len(kept[g]),
                         "n_pairs_both_cs_proxy": sum(s == "both_cs" for _, s in states),
                         "n_pairs_unknown": sum(s == "unknown" for _, s in states),
                         "classification": cl, "discordant_proxy": disc, "source_arms": ";".join(arms)})
    return rows


def proxy_totals(rows):
    """{contrast: likely/unknown/unlikely region counts, k (exact, or 'unknown'), k_true, k_unknown}."""
    out = {}
    for c in PROXY:
        rs = [r for r in rows if r["contrast"] == c]
        t = {k: sum(r["classification"] == k for r in rs) for k in ("likely", "unknown", "unlikely")}
        t["k_true"] = sum(r["discordant_proxy"] == "true" for r in rs)
        t["k_unknown"] = sum(r["discordant_proxy"] == "unknown" for r in rs)
        t["k"] = t["k_true"] if t["k_unknown"] == 0 else "unknown"
        out[c] = t
    return out


def proxy_flags(totals):
    flags = []
    for c, t in totals.items():
        if t["likely"] < N_REGIONS_MIN:
            flags.append(f"FLAG FOR CARTER: n_regions_min {N_REGIONS_MIN} may yield NON_INFORMATIVE for {c} "
                         f"(likely {t['likely']}/10, unknown {t['unknown']})")
        tail = f"; the sign-flip test cannot reach alpha 0.025 with k < {N_REGIONS_MIN} (min p = 2/2^k)"
        if t["k"] != "unknown" and t["k"] < N_REGIONS_MIN:
            flags.append(f"FLAG FOR CARTER: likely discordant regions k = {t['k']} < {N_REGIONS_MIN} for {c}{tail}")
        elif t["k"] == "unknown" and t["k_true"] + t["k_unknown"] < N_REGIONS_MIN:
            flags.append(f"FLAG FOR CARTER: likely discordant regions k <= {t['k_true'] + t['k_unknown']} < "
                         f"{N_REGIONS_MIN} for {c} (k unknown: {t['k_true']} true, {t['k_unknown']} unknown){tail}")
    return flags


def write_tsv(rows, cols, out):
    for r in rows:
        if set(r) != set(cols):
            raise ValueError(f"row keys {sorted(set(r) ^ set(cols))} differ from the columns")
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows({c: ("" if r[c] is None else r[c]) for c in cols} for r in rows)


def driver_script(list_path, n_tasks, log_dir, repo, py):
    """sbatch array driver: one measurement per task (no Snakemake, no fire script)."""
    return "\n".join([
        "#!/bin/bash",
        "#SBATCH -J w3f5_elig",
        "#SBATCH -p compute",
        "#SBATCH -A clintonlab_cpu",
        "#SBATCH -q normal",
        "#SBATCH -t 01:00:00",
        "#SBATCH --mem=32G",
        "#SBATCH -c 1",
        "#SBATCH --constraint=cascadelake",
        f"#SBATCH --array=1-{n_tasks}",
        f"#SBATCH -o {log_dir}/%A_%a.out",
        f"#SBATCH -e {log_dir}/%A_%a.out",
        "set -euo pipefail",
        f"cd {repo}",
        'echo "w3f5_placement host=$(hostname) task=$SLURM_ARRAY_TASK_ID"',
        f'PYTHONPATH=src/python {py} -m ta_r4.measure_fit_eligibility run --list {list_path} '
        f'--task "$SLURM_ARRAY_TASK_ID"',
        "",
    ])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--rscript", required=True)
    r = sub.add_parser("run")
    r.add_argument("--list", required=True)
    r.add_argument("--task", type=int, required=True)
    s = sub.add_parser("summarise")
    s.add_argument("--out-dir", required=True)
    s.add_argument("--rscript", required=True)
    s.add_argument("--tsv", required=True)
    x = sub.add_parser("proxy")
    x.add_argument("--rscript", required=True)
    x.add_argument("--tsv", required=True)
    a = ap.parse_args(argv)

    if a.cmd == "plan":
        if not Path(a.rscript).is_absolute():
            raise SystemExit(f"--rscript {a.rscript} must be absolute (Rscript is not on PATH in Slurm jobs)")
        out_dir = _norm(a.out_dir)
        if Path(out_dir).exists() and any(Path(out_dir).iterdir()):
            raise SystemExit(f"{out_dir} is not empty; use a fresh out dir")
        ids = region_ids()
        lines = []
        for k in run_list():
            cmd = measurement_argv(*k, arm_config(k[0]), out_dir, a.rscript, region_id=ids[k[3]])
            bad = audit_argv(cmd, out_dir, k[0])
            if bad:
                raise SystemExit(f"{k}: {bad}")
            Path(out_dir, k[0]).mkdir(parents=True, exist_ok=True)
            lines.append(json.dumps(cmd))
        lst, logs = f"{out_dir}/runlist.jsonl", f"{out_dir}/logs"
        Path(logs).mkdir(parents=True, exist_ok=True)
        Path(lst).write_text("\n".join(lines) + "\n")
        drv = Path(out_dir, "run.sh")
        drv.write_text(driver_script(lst, len(lines), logs, os.getcwd(), sys.executable))
        drv.chmod(0o750)
        print(f"run list: {len(lines)} tasks -> {lst}; driver {drv}")
        return 0
    if a.cmd == "run":
        cmd = json.loads(Path(a.list).read_text().splitlines()[a.task - 1])
        print("argv", json.dumps(cmd), flush=True)
        print("inputs", json.dumps(write_inputs_record(cmd)), flush=True)
        env = dict(os.environ, PATH=f"{Path(cmd[2]).parent}:{os.environ['PATH']}")
        return subprocess.run(cmd, env=env).returncode
    if a.cmd == "summarise":
        rows = eligibility_table(summarise(a.out_dir, a.rscript, run_list()))
        write_tsv(rows, ELIG_COLS, a.tsv)
        print(f"rows {len(rows)} measured {sum(r['method'] == 'measured' for r in rows)} "
              f"not_eligible {sum(r['eligible'] == 'false' for r in rows)}")
        return 0
    rows = region_contribution_proxy(a.rscript)
    write_tsv(rows, PROXY_COLS, a.tsv)
    totals = proxy_totals(rows)
    for c, t in totals.items():
        print(c, json.dumps(t))
    for f in proxy_flags(totals):
        print(f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
