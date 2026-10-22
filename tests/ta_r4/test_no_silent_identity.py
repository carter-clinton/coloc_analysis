"""D-13: no R4 fit may silently run on an identity matrix or on an undeclared panel.

Unit layer: every silent-identity shape run_susie_rss.R can emit at exit 0 is injected
and must be rejected by name. Live layer (r4_heavy): every production fit JSON under
ta_r4.paths.result_dirs("fits") is re-validated in its arm's validator_mode.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ta_r4 import paths
from ta_r4.arms import ARMS

REPO = Path(__file__).resolve().parents[2]
PY = sys.executable

REGION = "FTO_16q12"
A3 = paths.panel_path("A3_1kg", REGION)
A2 = paths.panel_path("A2_identity", REGION)
MD5 = "0" * 32
SHA = "a" * 64


def _fit(declared=A3, **over):
    fit = {
        "trait": "hypertension", "ancestry": "EUR", "method": "susie", "region_id": REGION,
        "status": "ok", "ld_matrix": declared, "ld_file_declared": declared,
        "ld_authoritative": True, "ld_allele_aware": True,
        "ld_status": "ld_loaded;overlap_ok;59;0.983", "convergence_status": "converged_primary",
    }
    fit.update(over)
    return fit


def _receipt(declared=A3, arm="A3_1kg", **over):
    rc = {
        "declared": declared, "present": True, "md5": MD5, "sha256": SHA, "size_bytes": 10,
        "arm": arm, "stage": ARMS[arm]["stage"], "ancestry": "EUR", "region_safe": REGION,
    }
    rc.update(over)
    return rc


def _row(**over):
    row = {"ancestry": "EUR", "region_safe": REGION, "md5": MD5, "sha256": SHA}
    row.update(over)
    return row


def _vf():
    from ta_r4.validate_r4_fits import validate_fit
    return validate_fit


# ---------------------------------------------------------------- positives

POSITIVE = {
    "real_overlap_ok": ("real_ld", _fit(), _receipt(), _row()),
    "real_partial_overlap": ("real_ld", _fit(ld_status="ld_loaded;partial_overlap;30;0.400"), _receipt(), _row()),
    "identity_matched": ("identity_matched", _fit(A2), _receipt(A2, "A2_identity"), _row()),
}


@pytest.mark.parametrize("name", sorted(POSITIVE))
def test_valid_fit_passes(name):
    mode, fit, rc, row = POSITIVE[name]
    assert _vf()(fit, rc, row, mode) == []


# ---------------------------------------------------------------- injected silent shapes

_no_ld = _fit()
del _no_ld["ld_matrix"]

NEGATIVE = {
    # run_susie_rss.R :1112-1117, NULL-R branch: ld_source <- source %||% "identity"
    "null_R_identity": ("real_ld", _fit(ld_matrix="identity"), _receipt(), _row(), "LD_MATRIX_IDENTITY"),
    "null_R_null": ("real_ld", _fit(ld_matrix=None), _receipt(), _row(), "LD_MATRIX_IDENTITY"),
    # :1140-1148 ladder exhaustion: only convergence_status carries it here
    "identity_fallback": ("real_ld", _fit(convergence_status="converged_primary;identity_fallback"),
                          _receipt(), _row(), "IDENTITY_FALLBACK"),
    "ld_dir_missing_status": ("real_ld", _fit(status="ld_dir_missing"), _receipt(), _row(), "LD_DIR_MISSING"),
    "ld_dir_missing_ld_status": ("real_ld", _fit(ld_matrix="identity", ld_status="ld_dir_missing"),
                                 _receipt(), _row(), "LD_DIR_MISSING"),
    "ld_declared_absent": ("real_ld", _fit(ld_status="LD_DECLARED_ABSENT: declared=x"), _receipt(), _row(),
                           "LD_DECLARED_ABSENT"),
    "matrix_ne_declared": ("real_ld", _fit(ld_matrix="data/r4/ld/EUR_ukb337k_r4/FTO_16q12.rds"),
                           _receipt(), _row(), "LD_MATRIX_NE_DECLARED"),
    "not_authoritative": ("real_ld", _fit(ld_authoritative=False), _receipt(), _row(), "LD_NOT_AUTHORITATIVE"),
    "not_allele_aware": ("real_ld", _fit(ld_allele_aware=False), _receipt(), _row(), "LD_NOT_ALLELE_AWARE"),
    "md5_ne_manifest": ("real_ld", _fit(), _receipt(md5="1" * 32), _row(), "RECEIPT_MD5_NE_MANIFEST"),
    "ld_fields_missing": ("real_ld", _no_ld, _receipt(), _row(), "ALARM_LD_FIELDS_MISSING"),
    "afr_receipt_on_eur_fit": ("real_ld", _fit(), _receipt(ancestry="AFR"), _row(), "RECEIPT_ANCESTRY_MISMATCH"),
    "no_manifest_row": ("real_ld", _fit(), _receipt(), None, "MANIFEST_ROW_MISSING"),
    "receipt_absent": ("real_ld", _fit(), None, _row(), "RECEIPT_MISSING"),
    "receipt_panel_absent": ("real_ld", _fit(), _receipt(present=False, md5=None), _row(), "RECEIPT_PANEL_ABSENT"),
    "receipt_declared_ne_fit": ("real_ld", _fit(), _receipt(declared="data/r4/ld/other.rds"), _row(),
                                "RECEIPT_DECLARED_NE_FIT"),
    "ld_status_not_loaded": ("real_ld", _fit(ld_status="ld_overlap_insufficient"), _receipt(), _row(),
                             "LD_STATUS_NOT_LOADED"),
    "arm_mode_mismatch": ("real_ld", _fit(A2), _receipt(A2, "A2_identity"), _row(), "MODE_ARM_MISMATCH"),
    "identity_in_ld_status": ("real_ld", _fit(ld_status="ld_loaded;overlap_ok;59;0.983;fallback_identity"),
                              _receipt(), _row(), "IDENTITY_FALLBACK"),
    # identity_matched (A2)
    "a2_points_at_real_panel": ("identity_matched", _fit(A2, ld_matrix=A3), _receipt(A2, "A2_identity"), _row(),
                                "LD_MATRIX_NE_DECLARED"),
    "a2_sha256_ne_manifest": ("identity_matched", _fit(A2), _receipt(A2, "A2_identity", sha256="b" * 64), _row(),
                              "RECEIPT_SHA256_NE_MANIFEST"),
    "a2_null_R": ("identity_matched", _fit(A2, ld_matrix="identity"), _receipt(A2, "A2_identity"), _row(),
                  "LD_MATRIX_IDENTITY"),
    "a2_declared_real_panel": ("identity_matched", _fit(A3), _receipt(A3, "A2_identity"), _row(),
                               "DECLARED_NOT_ARM_PANEL"),
    "a2_identity_fallback": ("identity_matched", _fit(A2, convergence_status="non_converged;identity_fallback"),
                             _receipt(A2, "A2_identity"), _row(), "IDENTITY_FALLBACK"),
}


@pytest.mark.parametrize("name", sorted(NEGATIVE))
def test_silent_shape_rejected_by_name(name):
    mode, fit, rc, row, expected = NEGATIVE[name]
    violations = _vf()(copy.deepcopy(fit), copy.deepcopy(rc), copy.deepcopy(row), mode)
    assert expected in violations, violations


# ---------------------------------------------------------------- legacy_any and early exits

LEGACY = {
    "real": (_fit("data/r4/ld/legacy_repro/EUR/FTO_16q12.rds", ld_authoritative=False, ld_allele_aware=False),
             _receipt("data/r4/ld/legacy_repro/EUR/FTO_16q12.rds", "repro_routeC")),
    "identity_null_R": (_fit("x", ld_matrix="identity", ld_status="ld_overlap_insufficient"),
                        _receipt("x", "repro_routeC")),
    "identity_payload": (_fit("data/r4/ld/k2d_identity/EUR/FTO_16q12.rds", ld_status="identity"),
                         _receipt("data/r4/ld/k2d_identity/EUR/FTO_16q12.rds", "repro_k2d_routeC")),
    "missing": (_fit("x", ld_matrix="identity", ld_status="ld_dir_missing"),
                _receipt("x", "repro_routeC", present=False, md5=None)),
}


@pytest.mark.parametrize("cls", sorted(LEGACY))
def test_legacy_any_never_fails_but_classifies(cls):
    from ta_r4.validate_r4_fits import classify_fit
    fit, rc = LEGACY[cls]
    assert _vf()(fit, rc, None, "legacy_any") == []
    assert classify_fit(fit, rc) == cls


@pytest.mark.parametrize("mode", ["real_ld", "identity_matched", "legacy_any"])
@pytest.mark.parametrize("status", ["no_variants", "too_many_variants"])
def test_early_exit_is_not_a_violation(mode, status):
    from ta_r4.validate_r4_fits import classify_fit
    fit = {"trait": "t2d", "ancestry": "EUR", "status": status, "ld_dir": "x"}
    assert _vf()(fit, None, None, mode) == []
    assert classify_fit(fit, None) == "early_exit"


def test_unknown_mode_raises():
    with pytest.raises(ValueError):
        _vf()(_fit(), _receipt(), _row(), "anything")


# ---------------------------------------------------------------- manifest lookup

def _write(p: Path, text: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


HDR = "ancestry\tregion_safe\tpath\tmd5\tsha256\tsize_bytes\tn_var\tn_samples\tbuild\tsource\thas_ref_alt\n"


def test_manifest_lookup_by_ancestry_and_region(tmp_path):
    from ta_r4.validate_r4_fits import manifest_row
    m = _write(tmp_path / "m.tsv", HDR + f"EUR\t{REGION}\tp\t{MD5}\t{SHA}\t1\t1\t1\tb\ts\ttrue\n"
                                     f"AFR\t{REGION}\tp\t{'2' * 32}\t{SHA}\t1\t1\t1\tb\ts\ttrue\n")
    assert manifest_row(m, "EUR", REGION)["md5"] == MD5
    assert manifest_row(m, "AFR", REGION)["md5"] == "2" * 32
    assert manifest_row(m, "EUR", "NOPE") is None


@pytest.mark.parametrize("body", [
    HDR + f"EUR\t{REGION}\tp\t{MD5}\t{SHA}\t1\t1\t1\tb\ts\ttrue\n" * 2,   # duplicate key
    "region_safe\tmd5\n" + f"{REGION}\t{MD5}\n",                          # no ancestry column
])
def test_bad_manifest_is_an_error(tmp_path, body):
    from ta_r4.validate_r4_fits import ManifestError, manifest_row
    m = _write(tmp_path / "m.tsv", body)
    with pytest.raises(ManifestError):
        manifest_row(m, "EUR", REGION)


# ---------------------------------------------------------------- CLI

def _cli(*args, cwd=REPO / "src/python"):
    env = dict(os.environ, PYTHONPATH=str(REPO / "src/python"))
    return subprocess.run([PY, "-m", "ta_r4.validate_r4_fits", *map(str, args)],
                          cwd=cwd, env=env, capture_output=True, text=True)


def _cli_files(tmp_path, fit, rc):
    f = tmp_path / "x.json"
    r = tmp_path / "x.ld_receipt.json"
    f.write_text(json.dumps(fit))
    r.write_text(json.dumps(rc))
    m = _write(tmp_path / "m.tsv", HDR + f"EUR\t{REGION}\tp\t{MD5}\t{SHA}\t1\t1\t1\tb\ts\ttrue\n")
    return f, r, m


def test_cli_identity_fixture_exits_1_one_line_per_violation(tmp_path):
    f, r, m = _cli_files(tmp_path, _fit(ld_matrix="identity", ld_status="ld_dir_missing"), _receipt())
    p = _cli("--mode", "real_ld", "--fit", f, "--receipt", r, "--panel-manifest", m)
    assert p.returncode == 1, p.stdout + p.stderr
    lines = [ln for ln in p.stdout.splitlines() if ln.startswith("VIOLATION")]
    assert any("LD_MATRIX_IDENTITY" in ln for ln in lines)
    assert any("LD_DIR_MISSING" in ln for ln in lines)
    assert len(lines) == len({ln.split()[1] for ln in lines})


def test_cli_valid_exits_0(tmp_path):
    f, r, m = _cli_files(tmp_path, _fit(), _receipt())
    p = _cli("--mode", "real_ld", "--fit", f, "--receipt", r, "--panel-manifest", m)
    assert p.returncode == 0, p.stdout + p.stderr
    assert "violations=0" in p.stdout


def test_cli_early_exit_counted(tmp_path):
    f, r, m = _cli_files(tmp_path, {"ancestry": "EUR", "status": "too_many_variants"}, _receipt())
    p = _cli("--mode", "real_ld", "--fit", f, "--receipt", r, "--panel-manifest", m)
    assert p.returncode == 0, p.stdout + p.stderr
    assert "early_exit=1" in p.stdout


# ---------------------------------------------------------------- receipt writer

def _receipt_cli(tmp_path, *args):
    env = dict(os.environ, PYTHONPATH=str(REPO / "src/python"))
    return subprocess.run([PY, "-m", "ta_r4.write_ld_receipt", *map(str, args)],
                          cwd=tmp_path, env=env, capture_output=True, text=True)


def _panel_setup(tmp_path, arm="A3_1kg", md5=None, rows=1):
    panel = tmp_path / "panel.rds"
    panel.write_bytes(b"fixture panel bytes")
    real_md5 = hashlib.md5(panel.read_bytes()).hexdigest()
    real_sha = hashlib.sha256(panel.read_bytes()).hexdigest()
    m = _write(tmp_path / "man.tsv", HDR + f"EUR\t{REGION}\t{panel}\t{md5 or real_md5}\t{real_sha}\t19\t1\t1\tb\ts\ttrue\n" * rows)
    o1 = _write(tmp_path / "o1.yaml", "a: 1\n")
    o2 = _write(tmp_path / "o2.yaml", "b: 2\n")
    pol = _write(tmp_path / "pol.yaml", "susie: {L: 10}\n")
    base = ["--declared", panel, "--arm", arm, "--stage", ARMS[arm]["stage"], "--overlay-files", o1, o2,
            "--policy", pol, "--panel-manifest", m, "--ancestry", "EUR", "--region-safe", REGION,
            "--out", tmp_path / "out.ld_receipt.json"]
    return panel, real_md5, real_sha, base


def test_receipt_writer_real_ld(tmp_path):
    panel, md5, sha, args = _panel_setup(tmp_path)
    p = _receipt_cli(tmp_path, *args)
    assert p.returncode == 0, p.stdout + p.stderr
    rc = json.loads((tmp_path / "out.ld_receipt.json").read_text())
    assert rc["declared"] == str(panel) and rc["present"] is True
    assert rc["md5"] == md5 and rc["sha256"] == sha and rc["size_bytes"] == 19
    assert rc["overlay_sha256"] == hashlib.sha256(b"a: 1\nb: 2\n").hexdigest()
    assert rc["policy_sha256"] == hashlib.sha256(b"susie: {L: 10}\n").hexdigest()
    assert rc["panel_manifest_md5"] == hashlib.md5((tmp_path / "man.tsv").read_bytes()).hexdigest()
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert rc["git_sha"] == head
    assert (rc["arm"], rc["stage"], rc["ancestry"], rc["region_safe"]) == ("A3_1kg", "production", "EUR", REGION)
    assert rc["ld_source_class"] == "real"


@pytest.mark.parametrize("case", ["md5_mismatch", "no_row", "duplicate_key", "absent_panel",
                                  "legacy_flag_on_real_arm", "stage_mismatch"])
def test_receipt_writer_exits_3(tmp_path, case):
    panel, md5, sha, args = _panel_setup(tmp_path, md5=("f" * 32 if case == "md5_mismatch" else None),
                                         rows=(2 if case == "duplicate_key" else 1))
    if case == "no_row":
        args[args.index("--region-safe") + 1] = "OTHER"
    if case == "absent_panel":
        panel.unlink()
    if case == "legacy_flag_on_real_arm":
        args.append("--legacy-any")
    if case == "stage_mismatch":
        args[args.index("--stage") + 1] = "repro"
    p = _receipt_cli(tmp_path, *args)
    assert p.returncode == 3, (case, p.stdout, p.stderr)
    assert not (tmp_path / "out.ld_receipt.json").exists()


def test_receipt_writer_legacy_any_absent_panel(tmp_path):
    panel, md5, sha, args = _panel_setup(tmp_path, arm="repro_routeC")
    panel.unlink()
    p = _receipt_cli(tmp_path, *args, "--legacy-any")
    assert p.returncode == 0, p.stdout + p.stderr
    rc = json.loads((tmp_path / "out.ld_receipt.json").read_text())
    assert rc["present"] is False and rc["md5"] is None and rc["ld_source_class"] == "missing"


def test_receipt_writer_legacy_arm_requires_flag(tmp_path):
    panel, md5, sha, args = _panel_setup(tmp_path, arm="repro_routeC")
    panel.unlink()
    p = _receipt_cli(tmp_path, *args)  # no --legacy-any: a repro arm may not pass as real_ld
    assert p.returncode == 3, p.stdout + p.stderr


# ---------------------------------------------------------------- live gate (W5a enables)

def test_live_gate_dirs_are_result_dirs():
    from ta_r4.validate_r4_fits import production_fit_dirs
    dirs = production_fit_dirs()
    assert dirs == paths.result_dirs("fits")
    assert any("/A3_1kg_isect/" in d for d in dirs)
    assert not any("/repro_" in d for d in dirs)


@pytest.mark.r4_heavy
def test_live_r4_fits_have_no_identity():
    from ta_r4.validate_r4_fits import production_fit_dirs, validate_file
    existing = [d for d in production_fit_dirs() if (REPO / d).is_dir()]
    if not existing:
        pytest.skip("no production fits yet (W5a enables)")
    problems = []
    for d in existing:
        arm = Path(d).parts[3]
        fits = sorted(p for p in (REPO / d).glob("*.json") if not p.name.endswith(".ld_receipt.json"))
        if not fits:
            problems.append(f"{d}: existing arm dir with 0 fit JSONs")
            continue
        for f in fits:
            for v in validate_file(f, arm, root=REPO)[0]:
                problems.append(f"{f.relative_to(REPO)}: {v}")
    assert problems == []
