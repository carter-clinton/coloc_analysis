"""W3f 15.5: measure post-restriction variant counts without fitting (review N1 recount), and the
confirmatory-region contribution proxy from existing repro fits (N7). Pre-lock, read-only on inputs.

measurement_argv() is commands.fit_command() with three changes: SUSIE_MAX_VARIANTS=0 (every fit early-exits
after the panel restriction), an absolute Rscript, and an --output under data/r4/tmp/. It refuses anything else.

CLI (cwd = repo root, PYTHONPATH=src/python):
  plan      --out-dir D --rscript R               write D/runlist.jsonl + D/run.sh (sbatch array), print its length
  run       --list L --task N                     record input sha256, then run line N (1-based) of the list
  summarise --out-dir D --rscript R --tsv T       eligibility table: measured rows (exactly the run list) + bound rows
  proxy     --rscript R --tsv T [--exact-purity] [--asthma-fit-root D] [--fits-tsv F]
                                                  region-contribution proxy table, totals and FLAG lines

15.7h2: asthma_pilot_commands() builds the 20 pre-lock asthma repro fits (corrected asthma input, outputs under
data/r4/measure_asthma_fix/fits); --asthma-fit-root reads asthma from them; --exact-purity recomputes every fitted
object's set count with exact purity on the matrix it was scored on (DEC-2026-11-21-ta-r4-proxy-exact-purity-scored-matrix).
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
from ta_r4.arms import ARMS, POLICY_REPRO, production_arms

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


def _fit_states(rscript, keys, repo=".", where=None):
    """{key: fit_cs_state} from the RDS sets stored at fit time. where(key) -> (json, rds) repo-relative."""
    repo = Path(repo)
    where = where or (lambda k: (paths.fit_json(*k), paths.fit_rds(*k)))
    docs, rds = {}, {}
    for k in keys:
        j = repo / where(k)[0]
        docs[k] = json.loads(j.read_text()) if j.is_file() else None
        if docs[k] is not None and docs[k].get("status") not in EARLY:
            rds[k] = str(repo / where(k)[1])
    out = subprocess.run([rscript, "-e", _SETS_R, *rds.values()], check=True, capture_output=True,
                         text=True).stdout if rds else ""
    by_path = dict(ln.split("\t") for ln in out.splitlines())
    return {k: fit_cs_state(docs[k], None if k not in rds or by_path[rds[k]] == "NA" else int(by_path[rds[k]]))
            for k in keys}


# ---- 15.7h2: asthma pilot fits and exact purity on the scored matrix ------------------------------------------------

PILOT_ARMS = ("repro_routeC", "repro_k2d_routeC")
#: The corrected asthma EUR input (route r4; debug asthma-eur-grch38-mislabel).
ASTHMA_PILOT_SUMSTATS = paths.sumstats_path("asthma", "EUR", "A3_1kg")
RESULTS = f"{paths.R4}/results"
PURITY_TOL = 1e-12
SCORED = ("identity", "panel", "regularized", "panel_fallback")
FITS_COLS = ["arm", "trait", "region", "convergence_status", "n_sets_stored", "n_sets_exact", "n_sets_exact_alt",
             "n_sets_checked", "scored_matrix", "discriminating", "max_abs_purity_diff", "max_abs_resid"]
VARIANT_MATCH_R = "src/snakemake/scripts/ta_r4/variant_match.R"


class PurityIdentityError(RuntimeError):
    """No scored-matrix candidate reproduces a fit's stored sets, or another exact-purity STOP rule fired."""


def pilot_fit_json(root, arm, region_safe):
    return f"{_norm(root)}/proxy_asthma_{arm}/asthma.EUR.{region_safe}.json"


def _set_flag(cmd, flag, value):
    cmd[cmd.index(flag) + 1] = value


def _refuse_results(out):
    if _under(out, RESULTS):
        raise ValueError(f"output {out} lies under {RESULTS}")


def asthma_pilot_commands(region_ids, out_root, repo="."):
    """{(arm, region_safe): argv}: each repro arm's commands.fit_command for asthma EUR, with --sumstats the
    corrected asthma file and --output under out_root/proxy_asthma_<arm>/ (never under data/r4/results)."""
    out = {}
    for arm in PILOT_ARMS:
        cfg = arm_config(arm, repo)
        for g in sorted(region_ids):
            cmd = list(commands.fit_command(arm, "asthma", "EUR", g, cfg, region_id=region_ids[g]))
            _set_flag(cmd, "--sumstats", ASTHMA_PILOT_SUMSTATS)
            o = pilot_fit_json(out_root, arm, g)
            _refuse_results(o)
            _set_flag(cmd, "--output", o)
            out[(arm, g)] = cmd
    return out


def asthma_pilot_split_commands(region_ids, split_root, rscript, repo="."):
    """asthma_pilot_commands' argv with three changes: SUSIE_MAX_VARIANTS=0 (every run exits before fitting and
    records its pre-panel n_variants), Rscript -> the absolute rscript, --output -> split_root/<arm>/."""
    if not Path(rscript).is_absolute():
        raise ValueError(f"rscript {rscript} must be absolute (Rscript is not on PATH in Slurm jobs)")
    out = {}
    for (arm, g), pilot in asthma_pilot_commands(region_ids, "data/r4/measure_asthma_fix/fits", repo).items():
        cmd = list(pilot)
        if cmd[1] != f"SUSIE_MAX_VARIANTS={CAP}" or cmd[2] != "Rscript":
            raise ValueError(f"unexpected fit_command prefix {cmd[:3]}")
        cmd[1], cmd[2] = "SUSIE_MAX_VARIANTS=0", rscript
        o = f"{_norm(split_root)}/{arm}/asthma.EUR.{g}.json"
        _refuse_results(o)
        _set_flag(cmd, "--output", o)
        out[(arm, g)] = cmd
    return out


def regularization_eps(policy_path, repo="."):
    import yaml

    pol = yaml.safe_load((Path(repo) / policy_path).read_text()) or {}
    eps = (pol.get("susie") or {}).get("ld_regularization_eps")
    if eps is None:
        raise PurityIdentityError(f"PURITY_STOP: {policy_path} has no susie.ld_regularization_eps")
    return float(eps)


def credible_set(arm, repo="."):
    """The --credible-set value commands.fit_command passes for arm."""
    return float(str(arm_config(arm, repo).get("finemap", {}).get("credible_set", 0.95)))


_EXACT_R = r"""
suppressPackageStartupMessages({ library(data.table); library(jsonlite) })
a <- commandArgs(TRUE)
spec <- fromJSON(a[1], simplifyVector = FALSE)
source(spec$variant_match)
eps <- as.numeric(spec$eps); TOL <- as.numeric(spec$tol); tabix <- spec$tabix
STOP <- function(...) stop(paste0("PURITY_STOP: ", sprintf(...)), call. = FALSE)
`%||%` <- function(x, y) if (is.null(x)) y else x
# the pinned call: only Xcorr and min_abs_corr vary
pinned <- function(fit, X, cov, mac) susieR::susie_get_cs(fit, Xcorr = X, coverage = cov, min_abs_corr = mac,
  dedup = TRUE, squared = FALSE, check_symmetric = TRUE, n_purity = ncol(X))
comp <- function(fit, X, cov) {  # every included component (V > 1e-9, non-empty, not a dedup duplicate)
  g <- pinned(fit, X, cov, 0)
  if (is.null(g$cs)) return(list(idx = integer(0), pur = numeric(0), size = integer(0)))
  list(idx = as.integer(g$cs_index), pur = as.numeric(g$purity$min.abs.corr), size = as.integer(lengths(g$cs)))
}
check <- function(fit, cp, cov) {  # the identity check of a candidate, per stored set via sets$cs_index
  st <- fit$sets; ics <- susieR:::in_CS(fit$alpha, cov)
  sidx <- as.integer(st$cs_index %||% integer(0))
  if (length(st$cs) != length(sidx)) return(list(ok = FALSE, why = "sets$cs and sets$cs_index differ in length"))
  resid <- 0; checked <- integer(0); csize <- integer(0)
  for (j in seq_along(sidx)) {
    k <- sidx[j]; mem <- which(ics[k, ] != 0)
    if (!identical(as.integer(unname(st$cs[[j]])), as.integer(mem)))
      return(list(ok = FALSE, why = sprintf("stored set L%d is not the coverage set of component %d", k, k)))
    if (length(mem) <= 100) {
      p <- cp$pur[match(k, cp$idx)]
      if (is.na(p)) return(list(ok = FALSE, why = sprintf("stored set L%d is not an included component", k)))
      r <- abs(p - as.numeric(st$purity$min.abs.corr[j]))
      resid <- max(resid, r)
      if (r > TOL) return(list(ok = FALSE, why = sprintf("L%d purity residual %.3e", k, r)))
      checked <- c(checked, k); csize <- c(csize, length(mem))
    }
  }
  for (i in seq_along(cp$idx)) if (!(cp$idx[i] %in% sidx) && cp$size[i] <= 100 && cp$pur[i] >= 0.5)
    return(list(ok = FALSE, why = sprintf("unstored component %d has purity %.6f >= 0.5", cp$idx[i], cp$pur[i])))
  list(ok = TRUE, resid = resid, checked = checked, csize = csize)
}
creg <- function(R) {  # cov2cor(sym(R + eps I)); R_fit is exactly symmetric, so sym() is the identity here
  diag(R) <- diag(R) + eps
  stats::cov2cor((R + t(R)) / 2)
}
read_window <- function(d) {
  hdr <- strsplit(system(sprintf("gunzip -c %s | head -1", shQuote(d$sumstats)), intern = TRUE), "\t")[[1]]
  w <- system2(tabix, c(d$sumstats, sprintf("%s:%s-%s", d$chrom, d$start, d$end)), stdout = TRUE)
  ss <- if (length(w)) fread(text = paste(w, collapse = "\n"), header = FALSE, col.names = hdr,
                             colClasses = "character", sep = "\t") else
    as.data.table(setNames(replicate(length(hdr), character(0), simplify = FALSE), hdr))
  for (cn in c("REF", "ALT", "SNP_ID")) if (!cn %in% names(ss)) ss[, (cn) := NA_character_]
  ss[, POS := as.numeric(POS)]
  ss[SNP_ID == "" | SNP_ID == "NA", SNP_ID := NA_character_]
  ss[CHR == as.character(d$chrom) & POS >= as.numeric(d$start) & POS <= as.numeric(d$end)]
}
one <- function(f) {
  d <- fromJSON(f$json)
  fit <- readRDS(f$rds)
  cov <- fit$sets$requested_coverage
  if (is.null(cov) || !isTRUE(all.equal(as.numeric(cov), as.numeric(f$credible_set), tolerance = 0)))
    STOP("%s: sets$requested_coverage %s != --credible-set %s", f$label, format(cov %||% "NULL"), f$credible_set)
  conv <- as.character(d$convergence_status %||% "")
  base <- sub(";identity_fallback$", "", conv)
  P <- readRDS(d$ld_file_declared)
  # identity Xcorr iff the fit JSON records it; the recorded LD identity must agree with the declared panel
  ifb <- grepl("identity_fallback", conv)
  rec_id <- sub(";.*$", "", as.character(d$ld_status %||% "")) %in% c("identity", "ld_missing") ||
    isTRUE(d$ld_overlap_zero_fallback)
  panel_id <- isTRUE(P$use_identity) && is.null(P$R)
  if (!ifb && rec_id != panel_id)
    STOP("%s: recorded LD identity %s (ld_status %s, ld_overlap_zero_fallback %s) disagrees with the declared panel identity %s (%s)",
         f$label, rec_id, format(d$ld_status %||% "NULL"), format(d$ld_overlap_zero_fallback %||% "NULL"), panel_id,
         d$ld_file_declared)
  identity <- ifb || rec_id
  order <- if (identity) "identity" else switch(base,
    converged_primary = "panel", converged_max_iter = "panel", converged_regularized = "regularized",
    non_converged = c("regularized", "panel_fallback"),
    STOP("%s: unknown convergence_status %s", f$label, conv))
  n <- ncol(fit$alpha); nm <- colnames(fit$lbf_variable)
  cand <- sort(unique(as.integer(unlist(susieR::susie_get_cs(fit, coverage = cov)$cs))))
  row <- list(label = f$label, convergence_status = conv, n_sets_stored = length(fit$sets$cs))
  # map the candidate members to panel rows (15.7c resolve_fit_names, then position + alleles); none for the identity
  unmapped <- character(0); idx <- integer(0)
  if (!identity && length(cand)) {
    res <- resolve_fit_names(nm[cand], read_window(d), fread(d$variant_catalog_path, colClasses = "character"),
                             P$variants, isTRUE(f$allow_duplicate_rows))
    p <- panel_alleles(P$variants); pk <- paste(p$chr, p$pos, p$ref, p$alt, sep = ":")
    idx <- vapply(seq_len(nrow(res)), function(j) {
      if (res$status[j] != "ok") return(NA_integer_)
      h <- which(pk == paste(res$chr[j], res$pos[j], res$ref[j], res$alt[j], sep = ":"))
      if (!length(h)) h <- which(pk == paste(res$chr[j], res$pos[j], res$alt[j], res$ref[j], sep = ":"))
      if (length(h) == 1) h else NA_integer_
    }, integer(1))
    unmapped <- nm[cand][is.na(idx)]
  }
  if (length(unmapped)) {
    rm(P); gc(verbose = FALSE)
    return(c(row, list(scored_matrix = "unmapped", unmapped = paste(head(unmapped, 10), collapse = ","),
                       n_unmapped = length(unmapped))))
  }
  R_fit <- diag(n)
  if (!identity && !is.null(P$R) && length(cand)) {
    sub <- as.matrix(P$R)[idx, idx, drop = FALSE]
    sub <- (sub + t(sub)) / 2; diag(sub) <- 1
    R_fit[cand, cand] <- sub
    rm(sub)
  }
  rm(P); gc(verbose = FALSE)
  if (identical(order, "identity")) R_fit <- diag(n)
  X <- NULL; cp <- NULL; chk <- NULL; label <- NA_character_; why <- character(0)
  for (o in order) {
    X <- if (o == "regularized") creg(R_fit) else R_fit
    cp <- comp(fit, X, cov); chk <- check(fit, cp, cov)
    if (chk$ok) { label <- o; break }
    why <- c(why, sprintf("%s: %s", o, chk$why)); X <- NULL; gc(verbose = FALSE)
  }
  if (is.na(label)) STOP("%s (%s): no candidate matches the stored sets (%s)", f$label, conv,
                         paste(why, collapse = "; "))
  n_exact <- length(pinned(fit, X, cov, 0.5)$cs)
  if (n_exact != sum(cp$pur >= 0.5)) STOP("%s: pinned count %d != included components at 0.5", f$label, n_exact)
  multi <- chk$checked[chk$csize >= 2]
  discriminating <- length(multi) > 0
  diff <- NA_real_
  if (label == "identity") {
    n_alt <- n_exact
  } else if (label == "panel") {  # analytic: C_reg off-diagonals are R_fit's / (1 + eps)
    alt <- ifelse(cp$size == 1, cp$pur, cp$pur / (1 + eps))
    n_alt <- sum(alt >= 0.5)
    if (discriminating) diff <- max(abs(cp$pur - alt)[match(multi, cp$idx)])
  } else {  # the other candidate, built directly: R_fit for regularized, C_reg for panel_fallback
    rm(X); gc(verbose = FALSE)
    Xa <- if (label == "regularized") R_fit else creg(R_fit)
    ca <- comp(fit, Xa, cov)
    n_alt <- length(pinned(fit, Xa, cov, 0.5)$cs)
    if (discriminating) diff <- max(abs(cp$pur[match(multi, cp$idx)] - ca$pur[match(multi, ca$idx)]))
    rm(Xa)
  }
  if (!discriminating && n_alt != n_exact)
    STOP("%s (%s): not discriminating and n_sets_exact %d != n_sets_exact_alt %d", f$label, label, n_exact, n_alt)
  rm(R_fit); gc(verbose = FALSE)
  c(row, list(n_sets_exact = n_exact, n_sets_exact_alt = n_alt, n_sets_checked = length(chk$checked),
              scored_matrix = label, discriminating = discriminating, max_abs_purity_diff = diff,
              max_abs_resid = chk$resid))
}
out <- lapply(spec$fits, one)
writeLines(toJSON(out, auto_unbox = TRUE, digits = NA, na = "string"), a[2])
"""


def _exact_fit_states(rscript, docs, where, repo, policy_path, fits_tsv, pilot):
    """{key: exact set count, or None if unmapped} for every fitted key (docs[k] not early); writes fits_tsv."""
    repo = Path(repo)
    eps = regularization_eps(policy_path, repo)
    tabix = Path(rscript).parent / "tabix"
    if not tabix.is_file():
        raise PurityIdentityError(f"PURITY_STOP: no tabix next to {rscript}")
    fitted = [k for k in sorted(docs) if docs[k] is not None and docs[k].get("status") not in EARLY]
    spec = {"variant_match": str(REPO_VARIANT_MATCH), "eps": repr(eps), "tol": repr(PURITY_TOL), "tabix": str(tabix),
            "fits": [{"label": "|".join(k), "json": where(k)[0], "rds": where(k)[1],
                      "credible_set": repr(credible_set(k[0], repo)), "allow_duplicate_rows": k not in pilot}
                     for k in fitted]}
    import tempfile

    with tempfile.TemporaryDirectory(dir=repo) as td:
        sp, op, rp = Path(td, "spec.json"), Path(td, "out.json"), Path(td, "exact_purity.R")
        sp.write_text(json.dumps(spec))
        rp.write_text(_EXACT_R)  # a script file: Rscript -e would join the lines and a comment would swallow the rest
        env = dict(os.environ, PATH=f"{Path(rscript).parent}:{os.environ.get('PATH', '')}")
        p = subprocess.run([rscript, str(rp), str(sp), str(op)], cwd=repo, env=env, capture_output=True,
                           text=True) if fitted else None
        if p is not None and (p.returncode != 0 or not op.is_file()):
            raise PurityIdentityError(p.stderr[-4000:])
        res = json.loads(op.read_text()) if fitted else []
    by = dict(zip(fitted, res))
    rows, states = [], {}
    for k, r in by.items():
        if r["scored_matrix"] == "unmapped":
            print(f"UNKNOWN (unmapped candidate members: {r['n_unmapped']}; first {r['unmapped']}): {r['label']}")
            states[k] = None
        else:
            states[k] = int(r["n_sets_exact"])
        rows.append({"arm": k[0], "trait": k[1], "region": k[3], "convergence_status": r["convergence_status"],
                     "n_sets_stored": r["n_sets_stored"], "n_sets_exact": r.get("n_sets_exact", ""),
                     "n_sets_exact_alt": r.get("n_sets_exact_alt", ""), "n_sets_checked": r.get("n_sets_checked", ""),
                     "scored_matrix": r["scored_matrix"],
                     "discriminating": "" if "discriminating" not in r else str(bool(r["discriminating"])),
                     "max_abs_purity_diff": "" if r.get("max_abs_purity_diff") in (None, "NA") else
                     repr(float(r["max_abs_purity_diff"])),
                     "max_abs_resid": "" if r.get("max_abs_resid") in (None, "NA") else repr(float(r["max_abs_resid"]))})
    if fits_tsv is not None:
        write_tsv(rows, FITS_COLS, fits_tsv)
    return states


REPO_VARIANT_MATCH = Path(__file__).resolve().parents[3] / VARIANT_MATCH_R


def _coloc_doc(repo, arm, region, a, b):
    p = Path(repo) / repro_coloc_json(arm, region, a, b)
    return json.loads(p.read_text()) if p.is_file() else None


def region_contribution_proxy(rscript, repo=".", exact_purity=False, asthma_fit_root=None, fits_tsv=None,
                              policy_path=POLICY_REPRO):
    """Per confirmatory region and contrast: proxy both-have-CS pairs from repro fits, classification, and the
    discordance proxy from repro coloc outputs. Default: asthma pairs excluded (their repro inputs are mislocated),
    set counts as stored at fit time. asthma_fit_root: asthma read from the pilot fits there, nothing excluded.
    exact_purity: every fitted object's count recomputed with exact purity on its scored matrix (fits_tsv rows)."""
    pairs = confirmatory_pairs(repo)
    excluded = () if asthma_fit_root is not None else PROXY_EXCLUDED_TRAITS
    kept = {g: [p for p in ps if not set(p) & set(excluded)] for g, ps in pairs.items()}
    keys = {(a, t, "EUR", g) for arms in PROXY.values() for a in arms for g, ps in kept.items() for p in ps for t in p}
    pilot = {k for k in keys if asthma_fit_root is not None and k[1] == "asthma"}

    def where(k):
        if k in pilot:
            j = pilot_fit_json(asthma_fit_root, k[0], k[3])
            return j, j[: -len(".json")] + ".fit.rds"
        return paths.fit_json(*k), paths.fit_rds(*k)

    if exact_purity:
        docs = {}
        for k in sorted(keys):
            j = Path(repo) / where(k)[0]
            docs[k] = json.loads(j.read_text()) if j.is_file() else None
        ex = _exact_fit_states(rscript, docs, where, repo, policy_path, fits_tsv, pilot)
        st = {k: (fit_cs_state(docs[k], 0) if k not in ex else ex[k]) for k in docs}
    else:
        st = _fit_states(rscript, sorted(keys), repo, where)
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


def _parser():
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
    x.add_argument("--exact-purity", action="store_true")
    x.add_argument("--asthma-fit-root")
    x.add_argument("--fits-tsv")
    return ap


def main(argv=None):
    a = _parser().parse_args(argv)

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
    if a.exact_purity and not a.fits_tsv:
        raise SystemExit("--exact-purity needs --fits-tsv")
    if a.exact_purity and not Path(a.rscript).is_absolute():
        raise SystemExit(f"--rscript {a.rscript} must be absolute")
    rows = region_contribution_proxy(a.rscript, exact_purity=a.exact_purity, asthma_fit_root=a.asthma_fit_root,
                                     fits_tsv=a.fits_tsv)
    write_tsv(rows, PROXY_COLS, a.tsv)
    totals = proxy_totals(rows)
    for c, t in totals.items():
        print(c, json.dumps(t))
    for f in proxy_flags(totals):
        print(f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
