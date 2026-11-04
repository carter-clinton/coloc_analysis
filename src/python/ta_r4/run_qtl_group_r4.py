"""Run every config/ta_r4/qtl_manifest.tsv row of one (qtl_arm, region, source, qtd) group (W3e; D-02, D-06, D-22).

Per row: run_qtl_coloc.R (the arm's flags); when either side has 0 credible sets, the labelled fallback_abf from
run_coloc_pair_r4.R --mode qtl_abf on the same bridged variant set. Row JSONs are {out_dir}/{qtl_row_id}.json; the
group ends with a coverage check against the manifest (exit 1 on any missing or extra row).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

from ta_r4 import paths
from ta_r4.arms import ARMS
from ta_r4.commands import COLOC_PRIORS, COLOC_SCRIPT, TRAIT_MANIFEST
from ta_r4.harmonize_qtl_r4 import MANIFEST, QTL_SOURCES, group_index, harmonized_path, manifest_rows, tissue_n

QTL_SCRIPT = "src/snakemake/scripts/run_qtl_coloc.R"
QTL_ARMS = {
    "QTL_A3": {"fit_arm": "A3_1kg", "ld_allele_join": "true", "qtl_orient": "true"},
    "QTL_A2": {"fit_arm": "A2_identity", "ld_allele_join": "true", "qtl_orient": "true"},
    # the pre-fix argv (E7): no --variant-list, no --qtl-orient, as qtl_coloc.smk rendered it for EUR
    "QTL_legacy": {"fit_arm": "repro_routeL", "ld_allele_join": "false", "qtl_orient": None},
}
SOURCE_KEY = {"eqtl": "gtex_eqtl", "sqtl": "gtex_sqtl"}
ANCESTRY = "EUR"
P12_KEY = "p12_primary"
#: run_qtl_coloc.R calls coloc.susie() with the package defaults; the runner refuses a priors yaml that differs.
COLOC_SUSIE_DEFAULTS = {"p1": 1e-4, "p2": 1e-4, "p12": 5e-6, "overlap_min": 0.5, "trim_by_posterior": True}
#: LD_JOIN_FATAL reasons that are a property of the data (too few bridged rows), recorded as a row status.
BELOW_FLOOR = ("panel_bridge_below_threshold", "qtl_orient_below_threshold")
NO_CS = ("no_qtl_cs", "no_gwas_cs")


def fit_arm(qtl_arm):
    return QTL_ARMS[qtl_arm]["fit_arm"]


def qtl_arm_for(arm):
    """The QTL arm run inside `arm`'s invocation, or None."""
    hit = [q for q, v in QTL_ARMS.items() if v["fit_arm"] == arm]
    return hit[0] if hit else None


def out_dir(qtl_arm):
    return f"{paths.R4}/results/{qtl_arm}/qtl"


def done_path(qtl_arm, region, source, qtd):
    return f"{out_dir(qtl_arm)}/{region}.{source}.{qtd}.done"


def catalog(qtl_arm, region):
    return paths.catalog_path(ARMS[fit_arm(qtl_arm)]["route"], region)


def region_ids(regions_csv=None):
    """{region_safe: region_id} by the Snakefile safe-id rule (regions_r4.csv has no duplicate safe ids)."""
    with open(regions_csv or paths.regions_csv(), newline="") as fh:
        ids = [r["region_id"] for r in csv.DictReader(fh)]
    out = {i.replace(".", "_").replace("/", "_"): i for i in ids}
    if len(out) != len(ids):
        raise ValueError("duplicate safe region ids")
    return out


def priors(path=COLOC_PRIORS):
    with open(path) as fh:
        y = yaml.safe_load(fh)
    p = {"p1": y["p1"], "p2": y["p2"], "p12": y[P12_KEY], "overlap_min": y["overlap_min"],
         "trim_by_posterior": y["trim_by_posterior"]}
    if p != COLOC_SUSIE_DEFAULTS:
        raise ValueError(f"{path} {p} != the coloc.susie defaults run_qtl_coloc.R uses {COLOC_SUSIE_DEFAULTS}")
    return {**p, "p12_key": P12_KEY}


def qtl_sdy(source, cfg_path=QTL_SOURCES):
    with open(cfg_path) as fh:
        return float(yaml.safe_load(fh)["sources"][SOURCE_KEY[source]]["sdY"])


def qtl_command(qtl_arm, row, output, sdy):
    a = QTL_ARMS[qtl_arm]
    fa, reg = a["fit_arm"], row["region_safe"]
    cmd = ["Rscript", QTL_SCRIPT,
           "--gwas-fit", paths.fit_rds(fa, row["trait"], ANCESTRY, reg),
           "--qtl-sumstats", harmonized_path(row["source"], row["qtd"], row["molecular_trait_id"], reg),
           "--ld-matrix", paths.panel_path(fa, reg, ANCESTRY),
           "--qtl-source", SOURCE_KEY[row["source"]], "--tissue", row["tissue"],
           "--gene-id", row["molecular_trait_id"], "--region", reg, "--ancestry", ANCESTRY,
           "--sdy", repr(sdy), "--sample-size", str(tissue_n(row["tissue"])),
           "--policy", ARMS[fa]["policy"], "--ld-allele-join", a["ld_allele_join"]]
    if a["ld_allele_join"] == "true":
        cmd += ["--variant-list", catalog(qtl_arm, reg)]
    if a["qtl_orient"] is not None:
        cmd += ["--qtl-orient", a["qtl_orient"]]
    return cmd + ["--output", output]


def abf_command(qtl_arm, row, region_id, output, sdy, reason):
    a = QTL_ARMS[qtl_arm]
    fa, reg = a["fit_arm"], row["region_safe"]
    cmd = ["Rscript", COLOC_SCRIPT, "--mode", "qtl_abf",
           "--gwas-fit", paths.fit_rds(fa, row["trait"], ANCESTRY, reg),
           "--sumstats-a", paths.sumstats_path(row["trait"], ANCESTRY, fa), "--trait-a", row["trait"],
           "--ancestry", ANCESTRY, "--region-id", region_id, "--regions-csv", paths.regions_csv(),
           "--trait-manifest", TRAIT_MANIFEST, "--priors", COLOC_PRIORS, "--p12-key", P12_KEY,
           "--qtl-sumstats", harmonized_path(row["source"], row["qtd"], row["molecular_trait_id"], reg),
           "--ld-matrix", paths.panel_path(fa, reg, ANCESTRY),
           "--ld-allele-join", a["ld_allele_join"], "--qtl-orient", a["qtl_orient"] or "false",
           "--sdy", repr(sdy), "--sample-size", str(tissue_n(row["tissue"])),
           "--fallback-reason", reason, "--row-id", row["qtl_row_id"], "--arm", qtl_arm, "--output", output]
    if a["ld_allele_join"] == "true":
        cmd += ["--variant-list", catalog(qtl_arm, reg)]
    return cmd


def fallback_reason(d):
    """'gwas_n_cs==0', 'qtl_n_cs==0' or both joined by '&', from run_qtl_coloc.R's n_cs fields."""
    z = [k for k, n in (("gwas_n_cs==0", d.get("n_cs_gwas")), ("qtl_n_cs==0", d.get("n_cs_qtl"))) if n == 0]
    if not z:
        raise ValueError(f"status {d.get('status')} with n_cs_gwas={d.get('n_cs_gwas')} n_cs_qtl={d.get('n_cs_qtl')}")
    return "&".join(z)


def _best_pp(summary):
    if isinstance(summary, dict) and "PP.H4.abf" in summary:
        return [summary.get(f"PP.H{i}.abf") for i in range(5)]
    return [None] * 5


def run_row(qtl_arm, row, region_id, odir, tmpdir, pri, sdy, run=subprocess.run):
    """Write {odir}/{qtl_row_id}.json. Returns the method, or None when the row failed (no JSON is written)."""
    rid = row["qtl_row_id"]
    tmp_q, tmp_a = f"{tmpdir}/{rid}.qtl.json", f"{tmpdir}/{rid}.abf.json"
    argv = qtl_command(qtl_arm, row, tmp_q, sdy)
    p = run(argv, capture_output=True, text=True)
    doc = {"qtl_row_id": rid, "qtl_arm": qtl_arm, "fit_arm": fit_arm(qtl_arm),
           **{k: row[k] for k in ("region_safe", "trait", "source", "tissue", "qtd", "molecular_trait_id")},
           "ensembl_gene_id": row["gene_id"], "argv": argv, "priors": pri, "fallback_reason": None,
           "fallback_argv": None}
    if p.returncode != 0:
        m = re.search(r"LD_JOIN_FATAL reason=(\S+)", p.stderr)
        if not (m and m.group(1) in BELOW_FLOOR):
            sys.stderr.write(f"[run_qtl_group_r4] ROW FAILED {rid} rc={p.returncode}\n{p.stderr[-2000:]}\n")
            return None
        line = next(ln for ln in p.stderr.splitlines() if "LD_JOIN_FATAL" in ln)
        doc.update(status=f"ld_join_fatal:{m.group(1)}", message=line.strip(), method="none", summary=[])
    else:
        d = json.loads(Path(tmp_q).read_text())
        os.remove(tmp_q)
        doc.update(d)
        if d["status"] == "success":
            if not (d["n_cs_gwas"] > 0 and d["n_cs_qtl"] > 0):
                raise ValueError(f"{rid}: success with n_cs {d['n_cs_gwas']}/{d['n_cs_qtl']}")
            doc["method"] = "coloc_susie"
        elif d["status"] in NO_CS:
            reason = fallback_reason(d)
            fargv = abf_command(qtl_arm, row, region_id, tmp_a, sdy, reason)
            fp = run(fargv, capture_output=True, text=True)
            if fp.returncode != 0:
                sys.stderr.write(f"[run_qtl_group_r4] FALLBACK FAILED {rid}\n{fp.stderr[-2000:]}\n")
                return None
            fb = json.loads(Path(tmp_a).read_text())
            os.remove(tmp_a)
            if fb["n_snps"] != d["n_snps_overlap"]:
                sys.stderr.write(f"[run_qtl_group_r4] FALLBACK SET MISMATCH {rid}: abf n_snps {fb['n_snps']} != "
                                 f"run_qtl_coloc.R n_snps_overlap {d['n_snps_overlap']}\n")
                return None
            doc.update(method="fallback_abf", fallback_reason=reason, fallback_argv=fargv, fallback=fb)
        else:
            doc["method"] = "none"
    pp = [doc["fallback"][f"pp_h{i}"] for i in range(5)] if doc["method"] == "fallback_abf" else \
        _best_pp(doc.get("summary"))
    doc.update({f"pp_h{i}": v for i, v in enumerate(pp)})
    out = Path(odir) / f"{rid}.json"
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_text(json.dumps(doc, indent=1))
    os.replace(tmp, out)
    return doc["method"]


def group_rows(rows, region, source, qtd):
    return group_index(rows).get((source, qtd, region), [])


def coverage(odir, expected_ids):
    """(missing, extra) qtl_row_ids. Extra = JSONs in odir of the same (region, source, tissue) not in expected."""
    exp = set(expected_ids)
    keys = {tuple(i.split("__")[k] for k in (0, 3, 4)) for i in exp}
    if len(keys) != 1:
        raise ValueError(f"expected ids span {len(keys)} groups")
    reg, src, tis = keys.pop()
    got = set()
    for p in Path(odir).glob(f"{reg}__*.json"):
        parts = p.name[: -len(".json")].split("__")
        if len(parts) == 6 and (parts[0], parts[3], parts[4]) == (reg, src, tis):
            got.add(p.name[: -len(".json")])
    return sorted(exp - got), sorted(got - exp)


def run_group(qtl_arm, region, source, qtd, manifest=MANIFEST, odir=None, run=subprocess.run):
    rows = group_rows(manifest_rows(manifest), region, source, qtd)
    if not rows:
        raise ValueError(f"no manifest rows for {region} {source} {qtd}")
    odir = odir or out_dir(qtl_arm)
    tmpdir = f"{paths.R4}/tmp/qtl_runner/{qtl_arm}/{region}.{source}.{qtd}"
    Path(odir).mkdir(parents=True, exist_ok=True)
    Path(tmpdir).mkdir(parents=True, exist_ok=True)
    pri, sdy, rid = priors(), qtl_sdy(source), region_ids()[region]
    counts = {}
    for row in sorted(rows, key=lambda r: r["qtl_row_id"]):
        m = run_row(qtl_arm, row, rid, odir, tmpdir, pri, sdy, run=run)
        counts[m] = counts.get(m, 0) + 1
    missing, extra = coverage(odir, [r["qtl_row_id"] for r in rows])
    return counts, missing, extra


def gwas_coloc_table(qtl_arm, output, pair_manifest="config/ta_r4/pair_manifest.tsv", manifest=MANIFEST):
    """The trait-pair coloc rows assign_tiers.py reads (region, ancestry, PP.H4.abf): the fit arm's susie-mode
    p12_primary JSON of every admissible EUR pair_manifest row in a QTL manifest region."""
    regions = {r["region_safe"] for r in manifest_rows(manifest)}
    with open(pair_manifest, newline="") as fh:
        prs = [r for r in csv.DictReader(fh, delimiter="\t")
               if r["admissible"] == "true" and r["ancestry"] == ANCESTRY and r["region_safe"] in regions]
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["row_id", "region", "ancestry", "method", "PP.H4.abf"])
        for r in sorted(prs, key=lambda r: r["row_id"]):
            d = json.loads(Path(paths.coloc_json(fit_arm(qtl_arm), r["row_id"], P12_KEY)).read_text())
            w.writerow([r["row_id"], r["region_safe"], ANCESTRY, d["method"], d["pp_h4"]])
    return len(prs)


def coloc_inputs(qtl_arm, pair_manifest="config/ta_r4/pair_manifest.tsv", manifest=MANIFEST):
    regions = {r["region_safe"] for r in manifest_rows(manifest)}
    with open(pair_manifest, newline="") as fh:
        return sorted(paths.coloc_json(fit_arm(qtl_arm), r["row_id"], P12_KEY)
                      for r in csv.DictReader(fh, delimiter="\t")
                      if r["admissible"] == "true" and r["ancestry"] == ANCESTRY and r["region_safe"] in regions)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--qtl-arm", required=True, choices=sorted(QTL_ARMS))
    ap.add_argument("--region")
    ap.add_argument("--source", choices=sorted(SOURCE_KEY))
    ap.add_argument("--qtd")
    ap.add_argument("--manifest", default=MANIFEST)
    ap.add_argument("--out-dir")
    ap.add_argument("--done", help="written only when coverage passes")
    ap.add_argument("--gwas-coloc-table", help="write the assign_tiers --gwas-coloc table and exit")
    a = ap.parse_args(argv)
    if a.gwas_coloc_table:
        n = gwas_coloc_table(a.qtl_arm, a.gwas_coloc_table, manifest=a.manifest)
        print(f"[run_qtl_group_r4] {a.qtl_arm} gwas coloc table: {n} rows")
        return 0
    if not (a.region and a.source and a.qtd):
        ap.error("--region, --source and --qtd are required")
    counts, missing, extra = run_group(a.qtl_arm, a.region, a.source, a.qtd, manifest=a.manifest, odir=a.out_dir)
    print(f"[run_qtl_group_r4] {a.qtl_arm} {a.region} {a.source} {a.qtd} methods={counts}")
    if missing or extra:
        sys.stderr.write(f"[run_qtl_group_r4] COVERAGE FAILED missing={len(missing)} extra={len(extra)}\n")
        for i in missing:
            sys.stderr.write(f"  missing {i}\n")
        for i in extra:
            sys.stderr.write(f"  extra {i}\n")
        return 1
    if a.done:
        Path(a.done).write_text(json.dumps({"methods": counts, "n_rows": sum(counts.values())}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
