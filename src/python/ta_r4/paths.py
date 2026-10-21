"""Every R4 input/output path (repo-relative strings). Result globs go through result_dirs()."""
from __future__ import annotations

from ta_r4 import arms

R4 = "data/r4"
PHASE_DIR = ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission"
MAN = f"{PHASE_DIR}/manifests"
A1_COLOC_DIRS = (f"{R4}/results/A1_EUR/coloc", f"{R4}/results/A1_AFR/coloc")

#: Panel dirs holding several ancestries as {panel_dir}/{ancestry}/{region_safe}.rds
#: (the legacy loader's file.path(ld_dir, ancestry, region) layout).
MULTI_ANCESTRY_PANEL_DIRS = ("legacy_repro", "k2d_identity")


def _ancestry(arm, ancestry):
    ancs = arms.arm_ancestries(arm)
    if ancestry is None:
        if len(ancs) != 1:
            raise ValueError(f"{arm} spans {ancs}; pass ancestry")
        return ancs[0]
    if ancestry not in ancs:
        raise ValueError(f"{arm} has no {ancestry} ancestry ({ancs})")
    return ancestry


def panel_template(arm, ancestry=None):
    d = arms.ARMS[arm]["panel_dir"]
    if d in MULTI_ANCESTRY_PANEL_DIRS:
        return f"{R4}/ld/{d}/{_ancestry(arm, ancestry)}/{{region_safe}}.rds"
    return f"{R4}/ld/{d}/{{region_safe}}.rds"


def panel_path(arm, region_safe, ancestry=None):
    return panel_template(arm, ancestry).format(region_safe=region_safe)


def panel_manifest_path(arm, ancestry):
    d = arms.ARMS[arm]["panel_dir"]
    anc = _ancestry(arm, ancestry)
    if d == "legacy_repro" and anc == "AFR":
        return f"{MAN}/panels_legacy_repro_AFR.tsv"
    return f"{MAN}/panels_{d}.tsv"


def fit_json(arm, trait, anc, region_safe):
    return f"{R4}/results/{arm}/fine_mapping/susie/{trait}.{anc}.{region_safe}.json"


def fit_rds(arm, trait, anc, region_safe):
    return fit_json(arm, trait, anc, region_safe)[: -len(".json")] + ".fit.rds"


def ld_receipt_json(arm, trait, anc, region_safe):
    return fit_json(arm, trait, anc, region_safe)[: -len(".json")] + ".ld_receipt.json"


def sumstats_path(trait, anc, arm):
    if trait == "bmi" and anc == "EUR" and arms.ARMS[arm]["route"] == "r4":
        return f"{R4}/sumstats/bmi.EUR.r4_alleles.tsv.bgz"  # D-18
    return f"data/processed/sumstats_harmonized/{trait}.{anc}.tsv.bgz"


def catalog_path(route, region_safe):
    if route not in ("r4", "legacy"):
        raise ValueError(f"unknown route {route!r}")
    return f"{R4}/ld/variants_{route}/{region_safe}.tsv"


def coloc_json(arm_or_A1, row_id, p12_key, varset=None):
    if arm_or_A1 in ("A1_EUR", "A1_AFR"):
        if varset is None:
            raise ValueError("A1 coloc paths need a varset")
        return f"{R4}/results/{arm_or_A1}/coloc/{row_id}.{varset}.{p12_key}.json"
    if varset is not None:
        raise ValueError(f"varset applies to A1 only, not {arm_or_A1}")
    arms.ARMS[arm_or_A1]  # KeyError on an unknown arm
    return f"{R4}/results/{arm_or_A1}/coloc/{row_id}.{p12_key}.json"


def ld_dir_unused():
    """Points finemap.ld_reference_dir somewhere that MUST NOT exist."""
    return f"{R4}/ld_dir_unused"


def regions_csv():
    return "config/ta_r4/regions_r4.csv"


def result_dirs(kind):
    prod = sorted(arms.production_arms())
    if kind == "fits":
        return [f"{R4}/results/{a}/fine_mapping/susie" for a in prod]
    if kind == "coloc":
        return [f"{R4}/results/{a}/coloc" for a in prod] + list(A1_COLOC_DIRS)
    raise ValueError(f"unknown kind {kind!r}")
