"""argv for each step of rule r4_run_finemap. The rule joins these with shlex.join and the e2e tests run
them as-is, so the tests exercise exactly what the rule runs. All paths are repo-relative (cwd = repo)."""
from __future__ import annotations

import sys

from ld_read_path import ld_allele_aware, ld_file_authoritative
from ta_r4 import paths
from ta_r4.arms import ARMS, CURRENT_SCRIPT

SUSIE_MAX_VARIANTS = 16000  # finemap.smk params.susie_max_variants default
METHOD = "susie"
_PY = ["env", "PYTHONPATH=src/python", sys.executable, "-m"]


def _legacy(arm):
    return ARMS[arm]["validator_mode"] == "legacy_any"


def ld_dir(arm):
    """Production: a dir that must not exist (no --ld-dir fallback). Repro: the legacy {ld_dir}/{anc}/ layout."""
    if not _legacy(arm):
        return paths.ld_dir_unused()
    d = ARMS[arm]["panel_dir"]
    if d not in paths.MULTI_ANCESTRY_PANEL_DIRS:
        raise ValueError(f"{arm}: legacy panel dir {d} is not in the {{ld_dir}}/{{ancestry}}/ layout")
    return f"{paths.R4}/ld/{d}"


def fit_command(arm, trait, ancestry, region_safe, config, *, region_id=None):
    """The frozen script's argument list (finemap.smk run_finemap order), under SUSIE_MAX_VARIANTS."""
    row = ARMS[arm]
    script = row["script"]
    cmd = ["env", f"SUSIE_MAX_VARIANTS={SUSIE_MAX_VARIANTS}", "Rscript", script,
           "--sumstats", paths.sumstats_path(trait, ancestry, arm),
           "--trait", trait, "--ancestry", ancestry, "--method", METHOD,
           "--region", region_id or region_safe, "--regions-csv", paths.regions_csv(),
           "--ld-dir", ld_dir(arm)]
    if script == CURRENT_SCRIPT:
        auth, aware = ld_file_authoritative(ancestry, config), ld_allele_aware(ancestry, config)
        want = "false" if _legacy(arm) else "true"
        if (auth, aware) != (want, want):
            raise ValueError(f"{arm} {ancestry}: ld_authoritative={auth} ld_allele_aware={aware}, need {want}")
        cmd += ["--ld-file", paths.panel_path(arm, region_safe, ancestry),
                "--ld-authoritative", auth, "--ld-allele-aware", aware]
    cmd += ["--variant-list", paths.catalog_path(row["route"], region_safe),
            "--credible-set", str(config.get("finemap", {}).get("credible_set", 0.95)),
            "--policy", row["policy"],
            "--output", paths.fit_json(arm, trait, ancestry, region_safe)]
    return cmd


def receipt_command(arm, trait, ancestry, region_safe):
    cmd = _PY + ["ta_r4.write_ld_receipt",
                 "--declared", paths.panel_path(arm, region_safe, ancestry),
                 "--arm", arm, "--stage", ARMS[arm]["stage"],
                 "--overlay-files", "config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{arm}.yaml",
                 "--policy", ARMS[arm]["policy"],
                 "--panel-manifest", paths.panel_manifest_path(arm, ancestry),
                 "--ancestry", ancestry, "--region-safe", region_safe,
                 "--out", paths.ld_receipt_json(arm, trait, ancestry, region_safe)]
    return cmd + (["--legacy-any"] if _legacy(arm) else [])


def validate_command(arm, trait, ancestry, region_safe):
    return _PY + ["ta_r4.validate_r4_fits", "--mode", ARMS[arm]["validator_mode"],
                  "--fit", paths.fit_json(arm, trait, ancestry, region_safe),
                  "--receipt", paths.ld_receipt_json(arm, trait, ancestry, region_safe),
                  "--panel-manifest", paths.panel_manifest_path(arm, ancestry)]


COLOC_SCRIPT = "src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R"
COLOC_PRIORS = "config/ta_r4/coloc_priors.yaml"
TRAIT_MANIFEST = "config/ta_r4/trait_manifest.tsv"
P12_KEYS = ("p12_primary", "p12_sensitivity")
COLOC_MODES = ("susie", "A1_matched", "A1_allvars")
#: A1 runs inside the invocation of the arm whose fits bind its matched variant set (D-21).
A1_FIT_ARMS = {"A3_1kg": "EUR", "AFR661_A3": "AFR"}


def coloc_output(arm, row, p12_key, mode):
    if mode == "susie":
        return paths.coloc_json(arm, row["row_id"], p12_key)
    return paths.coloc_json(f"A1_{row['ancestry']}", row["row_id"], p12_key, mode.split("_", 1)[1])


def coloc_command(arm, row, p12_key, mode):
    """run_coloc_pair_r4.R for one pair_manifest row. `arm` owns the fits (A1: the A3 arm)."""
    if mode not in COLOC_MODES or p12_key not in P12_KEYS:
        raise ValueError(f"mode {mode!r} / p12_key {p12_key!r}")
    anc, reg = row["ancestry"], row["region_safe"]
    if mode != "susie" and A1_FIT_ARMS.get(arm) != anc:
        raise ValueError(f"A1 runs only within {A1_FIT_ARMS} for its ancestry, not {arm} {anc}")
    a, b = row["trait_a"], row["trait_b"]
    cmd = ["Rscript", COLOC_SCRIPT, "--mode", mode]
    if mode != "A1_allvars":
        cmd += ["--fit-a", paths.fit_rds(arm, a, anc, reg), "--fit-b", paths.fit_rds(arm, b, anc, reg)]
    out_arm = arm if mode == "susie" else f"A1_{anc}"
    return cmd + ["--sumstats-a", paths.sumstats_path(a, anc, arm), "--sumstats-b", paths.sumstats_path(b, anc, arm),
                  "--trait-a", a, "--trait-b", b, "--ancestry", anc, "--region-id", row["region_id"],
                  "--regions-csv", paths.regions_csv(), "--trait-manifest", TRAIT_MANIFEST,
                  "--priors", COLOC_PRIORS, "--p12-key", p12_key, "--row-id", row["row_id"], "--arm", out_arm,
                  "--output", coloc_output(arm, row, p12_key, mode)]
