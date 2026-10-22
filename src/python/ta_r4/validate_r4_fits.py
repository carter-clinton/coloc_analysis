"""D-13 enforcer: an R4 fit must have read its declared, manifest-matched panel.

run_susie_rss.R exits 0 on three silent identity shapes (NULL-R branch, ladder-exhaustion
identity_fallback, LD_DECLARED_ABSENT -> ld_dir_missing), so the exit code is not evidence.

    python -m ta_r4.validate_r4_fits --mode real_ld --fit X.json [--receipt X.ld_receipt.json] \
        [--panel-manifest M.tsv]

Exit 1 on any violation (one VIOLATION line each), else 0. Modes: real_ld | identity_matched |
legacy_any (legacy_any never fails on LD source; it records ld_source_class).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

from ta_r4 import paths
from ta_r4.arms import ARMS

MODES = ("real_ld", "identity_matched", "legacy_any")
EARLY_EXIT = ("no_variants", "too_many_variants")
LD_STATUS_RE = re.compile(r"^ld_loaded;(overlap_ok|partial_overlap);")
IDENTITY_MATRIX = (None, "identity", "identity_fallback")
MISSING_STATUS = ("ld_dir_missing", "ld_missing")


class ManifestError(ValueError):
    pass


def manifest_row(manifest_path, ancestry, region_safe):
    """The unique (ancestry, region_safe) row, or None. Duplicate key / no ancestry column raise."""
    with open(manifest_path, newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        if "ancestry" not in (reader.fieldnames or []) or "region_safe" not in reader.fieldnames:
            raise ManifestError(f"{manifest_path}: needs ancestry and region_safe columns")
        hits = [r for r in reader if (r["ancestry"], r["region_safe"]) == (ancestry, region_safe)]
    if len(hits) > 1:
        raise ManifestError(f"{manifest_path}: duplicate key ({ancestry}, {region_safe})")
    return hits[0] if hits else None


def classify_fit(fit, receipt):
    """early_exit | missing | identity_payload | identity_null_R | real | fields_missing."""
    if fit.get("status") in EARLY_EXIT:
        return "early_exit"
    if "ld_matrix" not in fit:
        return "fields_missing"
    ld_status = str(fit.get("ld_status") or "")
    if (receipt is not None and receipt.get("present") is False) or ld_status in MISSING_STATUS \
            or ld_status.startswith("LD_DECLARED_ABSENT"):
        return "missing"
    if fit.get("ld_matrix") not in IDENTITY_MATRIX and ld_status.startswith("identity"):
        return "identity_payload"  # k2d R=NULL use_identity payload: real path, status "identity"
    if fit.get("ld_matrix") in IDENTITY_MATRIX or "identity" in str(fit.get("convergence_status") or "") \
            or not LD_STATUS_RE.match(ld_status):
        return "identity_null_R"
    return "real"


def validate_fit(fit, receipt, manifest_row, mode):
    """Violation names (empty list = pass)."""
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}")
    if fit.get("status") in EARLY_EXIT or mode == "legacy_any":
        return []
    if "ld_matrix" not in fit:
        return ["ALARM_LD_FIELDS_MISSING"]

    v = []
    ld_matrix = fit.get("ld_matrix")
    declared = fit.get("ld_file_declared")
    ld_status = str(fit.get("ld_status") or "")
    conv = str(fit.get("convergence_status") or "")

    if ld_matrix in IDENTITY_MATRIX:
        v.append("LD_MATRIX_IDENTITY")
    if "identity_fallback" in conv or "fallback_identity" in ld_status or ld_matrix == "identity_fallback":
        v.append("IDENTITY_FALLBACK")
    if fit.get("status") in MISSING_STATUS or ld_status in MISSING_STATUS:
        v.append("LD_DIR_MISSING")
    if ld_status.startswith("LD_DECLARED_ABSENT"):
        v.append("LD_DECLARED_ABSENT")
    if not LD_STATUS_RE.match(ld_status):
        v.append("LD_STATUS_NOT_LOADED")
    scanned = [ld_status, conv] + ([str(ld_matrix)] if mode == "real_ld" else [])
    if any("identity" in s for s in scanned):
        v.append("IDENTITY_SUBSTRING")
    if ld_matrix != declared:
        v.append("LD_MATRIX_NE_DECLARED")
    if fit.get("ld_authoritative") is not True:
        v.append("LD_NOT_AUTHORITATIVE")
    if fit.get("ld_allele_aware") is not True:
        v.append("LD_NOT_ALLELE_AWARE")

    if receipt is None:
        v.append("RECEIPT_MISSING")
    else:
        arm = receipt.get("arm")
        if receipt.get("declared") != declared:
            v.append("RECEIPT_DECLARED_NE_FIT")
        if receipt.get("present") is not True:
            v.append("RECEIPT_PANEL_ABSENT")
        if receipt.get("ancestry") != fit.get("ancestry"):
            v.append("RECEIPT_ANCESTRY_MISMATCH")
        if arm not in ARMS or ARMS[arm]["validator_mode"] != mode:
            v.append("MODE_ARM_MISMATCH")
        else:
            try:
                expected = paths.panel_path(arm, receipt.get("region_safe"), receipt.get("ancestry"))
            except ValueError:
                expected = None
            if receipt.get("declared") != expected:
                v.append("DECLARED_NOT_ARM_PANEL")
        if manifest_row is None:
            v.append("MANIFEST_ROW_MISSING")
        else:
            if receipt.get("md5") != manifest_row.get("md5"):
                v.append("RECEIPT_MD5_NE_MANIFEST")
            if receipt.get("sha256") != manifest_row.get("sha256"):
                v.append("RECEIPT_SHA256_NE_MANIFEST")
    return v


def receipt_path_for(fit_path):
    fit_path = Path(fit_path)
    return fit_path.with_name(fit_path.name[: -len(".json")] + ".ld_receipt.json")


def validate_file(fit_path, arm, root=".", mode=None):
    """Validate one fit JSON with its sibling receipt and its arm's manifest. -> (violations, class)."""
    mode = mode or ARMS[arm]["validator_mode"]
    fit = json.loads(Path(fit_path).read_text())
    rp = receipt_path_for(fit_path)
    receipt = json.loads(rp.read_text()) if rp.exists() else None
    row = None
    if receipt is not None and mode != "legacy_any":
        mp = Path(root) / paths.panel_manifest_path(arm, receipt.get("ancestry"))
        if mp.exists():
            row = manifest_row(mp, receipt.get("ancestry"), receipt.get("region_safe"))
    return validate_fit(fit, receipt, row, mode), classify_fit(fit, receipt)


def production_fit_dirs():
    """The live gate's glob roots: every production arm from ARMS, never a hand-written list."""
    return paths.result_dirs("fits")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mode", required=True, choices=MODES)
    ap.add_argument("--fit", required=True)
    ap.add_argument("--receipt")
    ap.add_argument("--panel-manifest")
    a = ap.parse_args(argv)

    fit = json.loads(Path(a.fit).read_text())
    rp = Path(a.receipt) if a.receipt else receipt_path_for(a.fit)
    receipt = json.loads(rp.read_text()) if rp.exists() else None
    row = None
    if a.panel_manifest and receipt is not None and a.mode != "legacy_any":
        try:
            row = manifest_row(a.panel_manifest, receipt.get("ancestry"), receipt.get("region_safe"))
        except (ManifestError, OSError) as e:
            print(f"VIOLATION MANIFEST_UNREADABLE {e}")
            return 1
    violations = validate_fit(fit, receipt, row, a.mode)
    cls = classify_fit(fit, receipt)
    for name in violations:
        print(f"VIOLATION {name} fit={a.fit}")
    print(f"validate_r4_fits mode={a.mode} n=1 early_exit={int(cls == 'early_exit')} "
          f"ld_source_class={cls} violations={len(violations)}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
