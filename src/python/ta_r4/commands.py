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
